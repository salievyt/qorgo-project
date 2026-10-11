"""
Shared test fixtures and factories for Qorgo backend tests.
"""
import uuid
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ===== User Factories =====

@pytest.fixture
def user_data() -> dict:
    """Default user registration data."""
    return {
        'phone_number': '+996555123456',
        'email': 'test@qorgo.app',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
    }


@pytest.fixture
def second_user_data() -> dict:
    """Second user for multi-user tests."""
    return {
        'phone_number': '+996555789012',
        'email': 'test2@qorgo.app',
        'first_name': 'Test2',
        'last_name': 'User2',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
    }


@pytest.fixture
def user(db, user_data) -> User:
    """Create and return a verified user."""
    from accounts.models import PrivacySettings
    privacy = PrivacySettings.objects.create()
    user = User.objects.create_user(
        phone_number=user_data['phone_number'],
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        password=user_data['password'],
        privacy_settings=privacy,
    )
    return user


@pytest.fixture
def second_user(db, second_user_data) -> User:
    """Create and return a second verified user."""
    from accounts.models import PrivacySettings
    privacy = PrivacySettings.objects.create()
    user = User.objects.create_user(
        phone_number=second_user_data['phone_number'],
        email=second_user_data['email'],
        first_name=second_user_data['first_name'],
        last_name=second_user_data['last_name'],
        password=second_user_data['password'],
        privacy_settings=privacy,
    )
    return user


# ===== API Clients =====

@pytest.fixture
def api_client() -> APIClient:
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def auth_client(user) -> APIClient:
    """Return an authenticated API client with JWT token."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def second_auth_client(second_user) -> APIClient:
    """Return an authenticated API client for second user."""
    client = APIClient()
    refresh = RefreshToken.for_user(second_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# ===== Location Data =====

@pytest.fixture
def bishkek_location() -> dict:
    """Bishkek, Kyrgyzstan coordinates."""
    return {
        'latitude': 42.8746,
        'longitude': 74.5698,
        'accuracy': 10.0,
        'speed': 0.5,
        'battery_level': 85.0,
        'is_background': False,
    }


@pytest.fixture
def osh_location() -> dict:
    """Osh, Kyrgyzstan coordinates."""
    return {
        'latitude': 40.5133,
        'longitude': 72.8161,
        'accuracy': 15.0,
        'speed': 2.0,
        'battery_level': 60.0,
        'is_background': False,
    }


# ===== SOS Data =====

@pytest.fixture
def sos_alert_data(bishkek_location) -> dict:
    """Default SOS alert creation data."""
    return {
        'latitude': bishkek_location['latitude'],
        'longitude': bishkek_location['longitude'],
        'address': 'Chui Avenue, Bishkek',
        'trigger_method': 'sos_button',
        'battery_level': 75.0,
    }


# ===== Family Data =====

@pytest.fixture
def family_data() -> dict:
    """Default family creation data."""
    return {
        'name': 'My Family',
    }


# ===== Geofence Data =====

@pytest.fixture
def geofence_data(bishkek_location) -> dict:
    """Default geofence creation data."""
    return {
        'name': 'Home',
        'zone_type': 'home',
        'latitude': bishkek_location['latitude'],
        'longitude': bishkek_location['longitude'],
        'radius': 100.0,
        'address': 'Home address',
    }


# ===== Safety Timer Data =====

@pytest.fixture
def safety_timer_data(osh_location) -> dict:
    """Default safety timer creation data."""
    return {
        'destination_latitude': osh_location['latitude'],
        'destination_longitude': osh_location['longitude'],
        'destination_address': 'Osh, Kyrgyzstan',
        'estimated_arrival_minutes': 30,
        'auto_trigger_alert': False,
    }


# ===== Subscription Data =====

@pytest.fixture
def subscription_plan(db) -> 'SubscriptionPlan':
    """Create a premium monthly subscription plan."""
    from subscriptions.models import SubscriptionPlan
    plan, _ = SubscriptionPlan.objects.get_or_create(
        plan_type='premium_monthly',
        defaults={
            'name': 'Premium Monthly',
            'price_usd': 4.99,
            'price_som': 420.00,
            'max_family_members': 10,
            'history_retention_days': 365,
            'ai_safety_analysis': True,
            'video_recording': True,
            'cloud_backup': True,
            'priority_notifications': True,
        }
    )
    return plan


@pytest.fixture
def free_plan(db) -> 'SubscriptionPlan':
    """Create a free subscription plan."""
    from subscriptions.models import SubscriptionPlan
    plan, _ = SubscriptionPlan.objects.get_or_create(
        plan_type='free',
        defaults={
            'name': 'Free',
            'price_usd': 0,
            'price_som': 0,
            'max_family_members': 5,
            'history_retention_days': 7,
        }
    )
    return plan


@pytest.fixture
def safety_timer_model_data(safety_timer_data):
    """Model uses an absolute deadline; API accepts minutes until arrival."""
    from datetime import timedelta
    from django.utils import timezone
    data = dict(safety_timer_data)
    minutes = data.pop('estimated_arrival_minutes')
    data['estimated_arrival_at'] = timezone.now() + timedelta(minutes=minutes)
    return data
