"""
Tests for accounts app — User model, authentication, profile, emergency contacts.
"""
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from rest_framework import status
from accounts.models import PrivacySettings, EmergencyContact

User = get_user_model()


# ===== Model Tests =====

@pytest.mark.django_db
class TestUserModel:
    """Test User model creation and methods."""

    def test_create_user(self, user_data):
        user = User.objects.create_user(
            phone_number=user_data['phone_number'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password'],
        )
        assert user.phone_number == user_data['phone_number']
        assert user.email == user_data['email']
        assert user.check_password(user_data['password'])
        assert user.is_active is True
        assert user.is_premium is False
        assert user.fcm_tokens == []

    def test_user_str_representation(self, user):
        assert str(user) == f'Test User ({user.phone_number})'

    def test_user_ordering(self, user, second_user):
        users = User.objects.all()
        assert users[0] == second_user

    def test_username_field(self):
        assert User.USERNAME_FIELD == 'phone_number'

    def test_phone_number_unique(self, user):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                phone_number=str(user.phone_number),
                email='other@test.com',
                first_name='Other',
                last_name='User',
                password='other123',
            )


@pytest.mark.django_db
class TestPrivacySettings:
    """Test PrivacySettings model."""

    def test_create_defaults(self):
        settings = PrivacySettings.objects.create()
        assert settings.show_location is True
        assert settings.location_visibility == 'family'

    def test_choices(self):
        settings = PrivacySettings.objects.create(location_visibility='nobody')
        assert settings.location_visibility == 'nobody'


@pytest.mark.django_db
class TestEmergencyContact:
    """Test EmergencyContact through model."""

    def test_create_contact(self, user, second_user):
        contact = EmergencyContact.objects.create(
            user=user, contact=second_user,
            name='Emergency Contact', phone_number='+996555111111',
            relationship='spouse', priority=1,
        )
        assert contact.priority == 1
        assert contact.is_verified is False

    def test_priority_ordering(self, user, second_user):
        EmergencyContact.objects.create(
            user=user, contact=second_user,
            name='C', phone_number='+996555111111',
            relationship='friend', priority=3,
        )
        user3 = User.objects.create_user(
            phone_number='+996555333333', email='u3@t.com',
            first_name='U3', last_name='U3', password='p123',
            privacy_settings=PrivacySettings.objects.create(),
        )
        EmergencyContact.objects.create(
            user=user, contact=user3,
            name='A', phone_number='+996555222222',
            relationship='parent', priority=1,
        )
        contacts = EmergencyContact.objects.filter(user=user)
        assert contacts[0].priority == 1
        assert contacts[1].priority == 3

    def test_create_high_priority(self, user):
        contact = EmergencyContact.objects.create(
            user=user, contact=user,
            name='Test', phone_number='+996555111111',
            relationship='self', priority=99,
        )
        assert contact.priority == 99


# ===== API Tests =====

@pytest.mark.django_db
class TestRegistrationAPI:
    """Test user registration endpoint."""

    REGISTER_URL = '/api/v1/auth/register/'

    def test_successful_registration(self, api_client, user_data):
        response = api_client.post(self.REGISTER_URL, user_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert response.data['user']['phone_number'] == user_data['phone_number']

    def test_password_mismatch(self, api_client, user_data):
        data = {**user_data, 'password_confirm': 'DifferentPass123!'}
        response = api_client.post(self.REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_required_fields(self, api_client):
        response = api_client.post(self.REGISTER_URL, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_phone(self, api_client, user_data, user):
        data = {**user_data, 'email': 'different@test.com',
                'password': 'OtherPass123!', 'password_confirm': 'OtherPass123!'}
        response = api_client.post(self.REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    """Test login endpoint."""

    LOGIN_URL = '/api/v1/auth/login/'

    def test_successful_login(self, api_client, user, user_data):
        response = api_client.post(self.LOGIN_URL, {
            'phone_number': user_data['phone_number'],
            'password': user_data['password'],
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_invalid_password(self, api_client, user):
        response = api_client.post(self.LOGIN_URL, {
            'phone_number': str(user.phone_number),
            'password': 'wrong_password',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_nonexistent_user(self, api_client):
        response = api_client.post(self.LOGIN_URL, {
            'phone_number': '+996000000000',
            'password': 'password123',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_fields(self, api_client):
        response = api_client.post(self.LOGIN_URL, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOTPAPI:
    """Test OTP request and verification."""

    REQUEST_URL = '/api/v1/auth/otp/request/'
    VERIFY_URL = '/api/v1/auth/otp/verify/'

    def test_request_otp(self, api_client, settings):
        settings.DEBUG = True
        response = api_client.post(self.REQUEST_URL, {
            'phone_number': '+996555123456',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'otp' in response.data

    def test_verify_valid_otp(self, api_client, settings):
        settings.DEBUG = True
        otp_resp = api_client.post(self.REQUEST_URL, {
            'phone_number': '+996555000111',
        }, format='json')
        otp = otp_resp.data['otp']
        response = api_client.post(self.VERIFY_URL, {
            'phone_number': '+996555000111',
            'otp_code': otp,
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert response.data['is_new'] is True

    def test_verify_invalid_otp(self, api_client):
        response = api_client.post(self.VERIFY_URL, {
            'phone_number': '+996555000111',
            'otp_code': '000000',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfileAPI:
    """Test profile management endpoints."""

    PROFILE_URL = '/api/v1/profile/'

    def test_get_profile_authenticated(self, auth_client, user):
        response = auth_client.get(self.PROFILE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == str(user.phone_number)

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(self.PROFILE_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_client):
        response = auth_client.patch('/api/v1/profile/update/', {
            'first_name': 'Updated', 'city': 'Bishkek',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'

    def test_change_password_success(self, auth_client, user_data):
        response = auth_client.post('/api/v1/profile/change-password/', {
            'old_password': user_data['password'],
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_old(self, auth_client):
        response = auth_client.post('/api/v1/profile/change-password/', {
            'old_password': 'wrong_old',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestFCMTokenAPI:
    """Test FCM token management."""

    def test_update_token(self, auth_client):
        response = auth_client.post('/api/v1/profile/fcm-token/', {
            'token': 'fcm_token_123',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_remove_token(self, auth_client):
        auth_client.post('/api/v1/profile/fcm-token/', {'token': 'remove_me'}, format='json')
        response = auth_client.post('/api/v1/profile/fcm-token/remove/', {'token': 'remove_me'}, format='json')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestEmergencyContactAPI:
    """Test emergency contacts CRUD."""

    def test_create_contact(self, auth_client, second_user):
        response = auth_client.post('/api/v1/emergency-contacts/', {
            'name': 'Emergency Contact',
            'phone_number': str(second_user.phone_number),
            'relationship': 'spouse', 'priority': 1,
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Emergency Contact'

    def test_list_contacts(self, auth_client, user, second_user):
        EmergencyContact.objects.create(
            user=user, contact=second_user,
            name='Contact 1', phone_number='+996555111111',
            relationship='friend', priority=1,
        )
        response = auth_client.get('/api/v1/emergency-contacts/')
        assert response.status_code == status.HTTP_200_OK

    def test_contacts_isolated(self, auth_client, second_auth_client, user, second_user):
        EmergencyContact.objects.create(
            user=user, contact=second_user,
            name='My Contact', phone_number='+996555111111',
            relationship='friend', priority=1,
        )
        response = second_auth_client.get('/api/v1/emergency-contacts/')
        assert len(response.data['results']) == 0


@pytest.mark.django_db
class TestUserSearchAPI:
    """Test user search endpoint."""

    def test_search_excludes_self(self, auth_client, user):
        response = auth_client.get('/api/v1/users/search/', {'q': str(user.phone_number)})
        assert len(response.data['results']) == 0

    def test_search_no_query(self, auth_client):
        response = auth_client.get('/api/v1/users/search/')
        assert len(response.data['results']) == 0

    def test_search_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/users/search/', {'q': '+996'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_by_partial(self, auth_client, user, second_user):
        """Search by phone number suffix."""
        response = auth_client.get('/api/v1/users/search/', {'q': '+996'})
        # Should find at least other users (excludes self)
        assert response.status_code == status.HTTP_200_OK
