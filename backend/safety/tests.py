import uuid
from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from .models import Alert, Contact, Delivery, Journey
from .services import create_alert, process_deadlines, process_deliveries

class SafetyApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(phone_number='+996700000010', email='owner@example.invalid', password='Qorgo-82-Strong!')
        self.other = get_user_model().objects.create_user(phone_number='+996700000011', email='other@example.invalid', password='Qorgo-93-Strong!')
        self.client.force_authenticate(self.user)
        self.contact = Contact.objects.create(owner=self.user, name='Близкий', phone='+996700000000')
    def test_registration_validates_password(self):
        self.client = APIClient()
        self.assertEqual(self.client.post('/api/register/', {'email':'new@example.invalid','password':'123'}).status_code, 400)
        r = self.client.post('/api/register/', {'email':'new@example.invalid','password':'New-Qorgo-82-Strong!','name':'New'})
        self.assertEqual(r.status_code, 201)
        self.assertTrue(get_user_model().objects.get(email='new@example.invalid').check_password('New-Qorgo-82-Strong!'))
    def test_authentication_and_contact_ownership(self):
        self.client = APIClient()
        self.assertEqual(self.client.get('/api/contacts/').status_code, 401)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/contacts/').data, [])
        self.assertEqual(self.client.patch(f'/api/contacts/{self.contact.id}/', {'name':'bad'}).status_code, 404)
        a, _ = create_alert(self.user, uuid.uuid4())
        self.assertEqual(self.client.post(f'/api/alerts/{a.id}/resolve/').status_code, 404)
    def test_contact_crud_and_normalization(self):
        r = self.client.post('/api/contacts/', {'name':'Друг','phone':'+996 (701) 000-001'})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['phone'], '+996701000001')
        cid = r.data['id']
        self.assertEqual(self.client.patch(f'/api/contacts/{cid}/', {'name':'Новое имя'}).status_code, 200)
        self.assertEqual(self.client.delete(f'/api/contacts/{cid}/').status_code, 204)
    def test_sos_idempotence_and_recipient_snapshot(self):
        key = str(uuid.uuid4())
        r = self.client.post('/api/alerts/', {'request_id':key}, format='json')
        self.contact.delete()
        duplicate = self.client.post('/api/alerts/', {'request_id':key}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['id'], duplicate.data['id'])
        self.assertEqual(Alert.objects.count(), 1)
        self.assertEqual(Delivery.objects.count(), 1)
    def test_sos_requires_contacts_and_valid_coordinates(self):
        self.assertEqual(self.client.post('/api/alerts/', {'request_id':str(uuid.uuid4()),'latitude':91,'longitude':0}, format='json').status_code, 400)
        self.contact.delete()
        self.assertEqual(self.client.post('/api/alerts/', {'request_id':str(uuid.uuid4())}, format='json').status_code, 400)
    def test_only_one_active_timer_and_contact_retained(self):
        data = {'destination':'Дом','deadline':(timezone.now()+timedelta(minutes=10)).isoformat()}
        self.assertEqual(self.client.post('/api/journeys/',data).status_code, 201)
        self.assertEqual(self.client.post('/api/journeys/',data).status_code, 400)
        self.assertEqual(self.client.delete(f'/api/contacts/{self.contact.id}/').status_code, 400)
    def test_expiration_works_without_app_and_only_once(self):
        j = Journey.objects.create(owner=self.user,destination='Дом',deadline=timezone.now()-timedelta(seconds=1))
        process_deadlines(); process_deadlines(); j.refresh_from_db()
        self.assertEqual(j.state,'expired')
        self.assertEqual(Alert.objects.count(),1)
    def test_early_and_late_arrival(self):
        j = Journey.objects.create(owner=self.user,destination='Дом',deadline=timezone.now()+timedelta(minutes=5))
        self.assertEqual(self.client.post(f'/api/journeys/{j.id}/arrive/').data['state'],'arrived')
        self.assertEqual(Alert.objects.count(),0)
        j = Journey.objects.create(owner=self.user,destination='Дом',deadline=timezone.now()-timedelta(seconds=1))
        self.assertEqual(self.client.post(f'/api/journeys/{j.id}/arrive/').data['state'],'expired')
        self.assertEqual(Alert.objects.count(),1)
    @override_settings(TWILIO_ACCOUNT_SID='',TWILIO_AUTH_TOKEN='',TWILIO_FROM='',EMAIL_HOST='')
    def test_no_provider_does_not_claim_delivery(self):
        a,_ = create_alert(self.user,uuid.uuid4()); process_deliveries()
        self.assertEqual(a.deliveries.get().status,'unconfigured')
    @patch('safety.services.dispatch',return_value=('sms','provider-id'))
    def test_acceptance_is_not_delivery_and_not_resent(self,dispatch):
        a,_ = create_alert(self.user,uuid.uuid4()); process_deliveries(); process_deliveries()
        self.assertEqual(a.deliveries.get().status,'accepted')
        self.assertEqual(dispatch.call_count,1)
    @patch('safety.services.dispatch',side_effect=TimeoutError)
    def test_timeout_requires_explicit_retry(self,dispatch):
        a,_ = create_alert(self.user,uuid.uuid4()); process_deliveries(); process_deliveries()
        self.assertEqual(a.deliveries.get().status,'unknown')
        self.assertEqual(dispatch.call_count,1)
        self.client.post(f'/api/alerts/{a.id}/retry/')
        self.assertEqual(a.deliveries.get().status,'pending')
    @patch('safety.services.dispatch')
    def test_resolve_cancels_unsent_messages(self,dispatch):
        a,_ = create_alert(self.user,uuid.uuid4()); self.client.post(f'/api/alerts/{a.id}/resolve/'); process_deliveries()
        self.assertEqual(a.deliveries.get().status,'cancelled'); dispatch.assert_not_called()

class InAppSosTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.sender = User.objects.create_user(phone_number='+996700000091', email='sender@example.invalid', password='Qorgo-82-Strong!')
        self.recipient = User.objects.create_user(phone_number='+996700000092', email='recipient@example.invalid', password='Qorgo-93-Strong!')
        self.stranger = User.objects.create_user(phone_number='+996700000093', email='stranger@example.invalid', password='Qorgo-94-Strong!')
        Contact.objects.create(owner=self.sender, name='Receiver', phone='+996700000099', email='RECIPIENT@example.invalid')

    def test_sos_reaches_recipient_and_ack_is_visible_to_sender(self):
        self.client.force_authenticate(self.sender)
        alert = self.client.post('/api/alerts/', {'request_id': str(uuid.uuid4())}, format='json')
        self.assertEqual(alert.status_code, 201)
        self.client.force_authenticate(self.recipient)
        incoming = self.client.get('/api/inbox/').data
        self.assertEqual(len(incoming), 1)
        self.assertEqual(incoming[0]['alert']['id'], alert.data['id'])
        delivery_id = incoming[0]['delivery_id']
        self.assertEqual(self.client.post(f'/api/inbox/{delivery_id}/acknowledge/').status_code, 200)
        self.assertEqual(self.client.post(f'/api/inbox/{delivery_id}/acknowledge/').status_code, 200)
        self.client.force_authenticate(self.sender)
        self.assertEqual(self.client.get(f"/api/alerts/{alert.data['id']}/").data['deliveries'][0]['status'], 'received')

    def test_inbox_and_confirmation_are_private(self):
        alert, _ = create_alert(self.sender, uuid.uuid4())
        self.client.force_authenticate(self.stranger)
        self.assertEqual(self.client.get('/api/inbox/').data, [])
        self.assertEqual(self.client.post(f'/api/inbox/{alert.deliveries.get().id}/acknowledge/').status_code, 404)
        self.client.force_authenticate(self.recipient)
        self.assertEqual(self.client.post(f'/api/alerts/{alert.id}/resolve/').status_code, 404)

    def test_sender_resolution_remains_visible_to_recipient(self):
        alert, _ = create_alert(self.sender, uuid.uuid4())
        self.client.force_authenticate(self.sender)
        self.client.post(f'/api/alerts/{alert.id}/resolve/')
        self.client.force_authenticate(self.recipient)
        self.assertIsNotNone(self.client.get('/api/inbox/').data[0]['alert']['resolved_at'])

class PhoneContactTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(phone_number='+996700123450', email='lookup-owner@example.invalid', password='Qorgo-82-Strong!')
        self.friend = User.objects.create_user(phone_number='+996700123456', email='private-friend@example.invalid', first_name='Best Friend', password='Qorgo-83-Strong!')
        self.client.force_authenticate(self.owner)

    def test_exact_lookup_normalizes_local_phone_without_exposing_email(self):
        result = self.client.post('/api/contacts/lookup/', {'phone': '0700 123-456'}, format='json')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['phone'], '+996700123456')
        self.assertEqual(result.data['name'], 'Best Friend')
        self.assertNotIn('email', result.data)
        self.assertNotIn('id', result.data)
        self.assertFalse(result.data['already_added'])
        self.assertEqual(self.client.post('/api/contacts/lookup/', {'phone': '123'}, format='json').status_code, 400)

    def test_linked_friend_receives_sos_without_email_and_after_profile_change(self):
        result = self.client.post('/api/contacts/', {'name':'Local Alias', 'phone':str(self.friend.phone_number), 'link_registered':True}, format='json')
        self.assertEqual(result.status_code, 201)
        self.assertTrue(result.data['in_qorgo'])
        self.assertEqual(result.data['email'], '')
        self.assertEqual(Contact.objects.get(pk=result.data['id']).recipient, self.friend)
        self.assertTrue(self.client.post('/api/contacts/lookup/', {'phone':str(self.friend.phone_number)}, format='json').data['already_added'])
        self.assertEqual(self.client.post('/api/contacts/', {'name':'Duplicate','phone':str(self.friend.phone_number),'link_registered':True}, format='json').status_code, 400)
        alert = self.client.post('/api/alerts/', {'request_id':str(uuid.uuid4())}, format='json')
        self.assertEqual(alert.data['deliveries'][0]['status'], 'available')
        self.friend.email = 'changed-friend@example.invalid'
        self.friend.phone_number = '+996700123457'
        self.friend.save(update_fields=['email','phone_number'])
        self.client.force_authenticate(self.friend)
        incoming = self.client.get('/api/inbox/').data
        self.assertEqual(len(incoming), 1)
        self.assertEqual(incoming[0]['alert']['id'], alert.data['id'])
        self.assertEqual(self.client.post(f"/api/inbox/{incoming[0]['delivery_id']}/acknowledge/").status_code, 200)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.get(f"/api/alerts/{alert.data['id']}/").data['deliveries'][0]['status'], 'received')
        # Editing the local alias retains the account association.
        self.assertEqual(self.client.patch(f"/api/contacts/{result.data['id']}/", {'name':'New Alias'}, format='json').status_code, 200)
        self.assertEqual(Contact.objects.get(pk=result.data['id']).recipient, self.friend)

    def test_missing_blocked_deleted_and_own_phone_are_not_addable_as_registered(self):
        self.assertEqual(self.client.post('/api/contacts/lookup/', {'phone':str(self.owner.phone_number)}, format='json').status_code, 400)
        self.friend.is_active = False
        self.friend.save(update_fields=['is_active'])
        self.assertFalse(self.client.post('/api/contacts/lookup/', {'phone':str(self.friend.phone_number)}, format='json').data['registered'])
        self.assertEqual(self.client.post('/api/contacts/', {'name':'Blocked','phone':str(self.friend.phone_number),'link_registered':True}, format='json').status_code, 400)
        self.friend.is_active = True
        self.friend.is_deleted = True
        self.friend.save(update_fields=['is_active','is_deleted'])
        self.assertFalse(self.client.post('/api/contacts/lookup/', {'phone':str(self.friend.phone_number)}, format='json').data['registered'])

    def test_profile_number_can_be_saved_but_cannot_take_another_accounts_number(self):
        self.assertEqual(self.client.patch('/api/profile/', {'phone_number':'0700 123 459'}, format='json').data['phone_number'], '+996700123459')
        self.assertEqual(self.client.patch('/api/profile/', {'phone_number':str(self.friend.phone_number)}, format='json').status_code, 400)
        self.owner.refresh_from_db()
        self.assertEqual(str(self.owner.phone_number), '+996700123459')
        self.assertEqual(self.client.patch('/api/profile/', {'phone_number':''}, format='json').data['phone_number'], '')

    def test_lookup_requires_login(self):
        self.client = APIClient()
        self.assertEqual(self.client.post('/api/contacts/lookup/', {'phone':str(self.friend.phone_number)}, format='json').status_code, 401)

    def test_existing_contacts_can_be_linked_without_duplicate_account_associations(self):
        from django.apps import apps
        from django.db import connection
        from importlib import import_module
        from types import SimpleNamespace
        legacy = Contact.objects.create(owner=self.owner, name='Legacy Friend', phone=str(self.friend.phone_number))
        migrate = import_module('safety.migrations.0003_link_existing_phone_contacts').link_existing_contacts
        migrate(apps, SimpleNamespace(connection=connection))
        legacy.refresh_from_db()
        self.assertEqual(legacy.recipient, self.friend)
        # Re-running is harmless and a second old number does not create two links.
        other = Contact.objects.create(owner=self.owner, name='New Number', phone='+996700123459')
        self.friend.phone_number = other.phone
        self.friend.save(update_fields=['phone_number'])
        migrate(apps, SimpleNamespace(connection=connection))
        other.refresh_from_db()
        self.assertIsNone(other.recipient)
