import sqlite3
import tempfile
from pathlib import Path
from io import StringIO
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Contact, Alert, Delivery, Journey


class UnifiedAuthTests(APITestCase):
    def test_email_token_and_phone_jwt_share_user(self):
        User = get_user_model()
        user = User.objects.create_user(phone_number='+996700000022', email='both@example.invalid', password='Both-Qorgo-82-Strong!')
        response = self.client.post('/api/login/', {'email': user.email, 'password': 'Both-Qorgo-82-Strong!'})
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["token"]}')
        self.assertEqual(self.client.get('/api/profile/').data['email'], user.email)
        self.assertEqual(self.client.post('/api/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/profile/').status_code, 401)
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.assertEqual(self.client.get('/api/v1/profile/').status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_multiple_email_only_accounts_and_inactive_login(self):
        for email in ['first@example.invalid', 'second@example.invalid']:
            self.assertEqual(self.client.post('/api/register/', {'email': email, 'password': 'Both-Qorgo-82-Strong!'}).status_code, 201)
        user = get_user_model().objects.get(email='first@example.invalid')
        self.assertIsNone(user.phone_number)
        self.assertIsNotNone(user.privacy_settings)
        user.is_active = False
        user.save()
        self.assertEqual(self.client.post('/api/login/', {'email': user.email, 'password': 'Both-Qorgo-82-Strong!'}).status_code, 400)

    def test_v1_registration_still_requires_phone(self):
        response = self.client.post('/api/v1/auth/register/', {'email': 'v1@example.invalid', 'first_name': 'Test', 'last_name': 'User', 'password': 'Both-Qorgo-82-Strong!', 'password_confirm': 'Both-Qorgo-82-Strong!'}, format='json')
        self.assertEqual(response.status_code, 400)


class LegacyImportTests(APITestCase):
    def test_import_preserves_relations_token_password_and_source(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'legacy.sqlite3'
            password = get_user_model()(email='old@example.invalid')
            password.set_password('Old-Qorgo-82-Strong!')
            timestamp = '2026-10-11 10:00:00'
            with sqlite3.connect(source) as db:
                db.executescript('''
                    CREATE TABLE auth_user (id, username, email, password, first_name, last_name, is_active, is_staff, is_superuser, date_joined, last_login);
                    CREATE TABLE authtoken_token (key, user_id, created);
                    CREATE TABLE safety_contact (id, owner_id, name, phone, email, relationship);
                    CREATE TABLE safety_alert (id, owner_id, request_id, created_at, reason, latitude, longitude, location_at, location_accuracy, resolved_at);
                    CREATE TABLE safety_delivery (id, alert_id, name, phone, email, status, channel, provider_id, attempts, updated_at);
                    CREATE TABLE safety_journey (id, owner_id, destination, deadline, state, created_at, alert_id);
                ''')
                db.execute('INSERT INTO auth_user VALUES (1, ?, ?, ?, ?, ?, 1, 0, 0, ?, NULL)', ('old@example.invalid', 'old@example.invalid', password.password, 'Old', '', timestamp))
                db.execute('INSERT INTO authtoken_token VALUES (?, 1, ?)', ('a' * 40, timestamp))
                db.execute("INSERT INTO safety_contact VALUES (1, 1, 'Friend', '+996700000001', '', '')")
                db.execute("INSERT INTO safety_alert VALUES (1, 1, ?, ?, 'sos', NULL, NULL, NULL, NULL, NULL)", ('123456781234123412341234567890ab', timestamp))
                db.execute("INSERT INTO safety_delivery VALUES (1, 1, 'Friend', '+996700000001', '', 'accepted', 'sms', 'provider', 1, ?)", (timestamp,))
                db.execute("INSERT INTO safety_journey VALUES (1, 1, 'Home', ?, 'expired', ?, 1)", (timestamp, timestamp))
            original = source.read_bytes()
            call_command('import_legacy_backend', str(source), stdout=StringIO())
            user = get_user_model().objects.get(email='old@example.invalid')
            self.assertTrue(user.check_password('Old-Qorgo-82-Strong!'))
            self.assertEqual(Contact.objects.get().owner_id, user.pk)
            self.assertEqual(Journey.objects.get().alert_id, Alert.objects.get().pk)
            self.assertEqual(Delivery.objects.get().status, 'accepted')
            self.assertEqual(Alert.objects.get().created_at.isoformat(), '2026-10-11T10:00:00+00:00')
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + 'a' * 40)
            self.assertEqual(client.get('/api/profile/').status_code, 200)
            with self.assertRaises(CommandError):
                call_command('import_legacy_backend', str(source), stdout=StringIO())
            self.assertEqual(source.read_bytes(), original)
