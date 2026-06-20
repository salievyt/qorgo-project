"""
Tests for safety_timers app — "I should arrive by" safety timer lifecycle.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from safety_timers.models import SafetyTimer


class TestSafetyTimerModel:
    """Test SafetyTimer model."""

    def test_create_timer(self, user, safety_timer_data):
        timer = SafetyTimer.objects.create(
            user=user,
            **safety_timer_data,
        )
        assert timer.status == SafetyTimer.Status.ACTIVE
        assert timer.destination_address == 'Osh, Kyrgyzstan'
        assert timer.auto_trigger_alert is False
        assert str(timer).startswith(f'{user}')
        assert 'Osh' in str(timer)

    def test_mark_arrived(self, user, safety_timer_data):
        timer = SafetyTimer.objects.create(user=user, **safety_timer_data)
        timer.status = SafetyTimer.Status.ARRIVED
        timer.save()
        assert timer.status == 'arrived'

    def test_mark_missed(self, user, safety_timer_data):
        timer = SafetyTimer.objects.create(user=user, **safety_timer_data)
        timer.status = SafetyTimer.Status.MISSED
        timer.save()
        assert timer.status == 'missed'

    def test_cancel_timer(self, user, safety_timer_data):
        timer = SafetyTimer.objects.create(user=user, **safety_timer_data)
        timer.status = SafetyTimer.Status.CANCELLED
        timer.save()
        assert timer.status == 'cancelled'

    def test_timer_auto_trigger(self, user):
        timer = SafetyTimer.objects.create(
            user=user,
            destination_latitude=42.0,
            destination_longitude=74.0,
            destination_address='Test',
            estimated_arrival_at=timezone.now() + timedelta(hours=1),
            auto_trigger_alert=True,
        )
        assert timer.auto_trigger_alert is True

    def test_timer_ordering(self, user):
        t1 = SafetyTimer.objects.create(
            user=user, destination_latitude=42.0, destination_longitude=74.0,
            destination_address='A', estimated_arrival_at=timezone.now() + timedelta(hours=1),
        )
        t2 = SafetyTimer.objects.create(
            user=user, destination_latitude=43.0, destination_longitude=75.0,
            destination_address='B', estimated_arrival_at=timezone.now() + timedelta(hours=2),
        )
        timers = SafetyTimer.objects.all()
        assert timers[0] == t2  # Most recent first
        assert timers[1] == t1


# ===== API Tests =====

class TestSafetyTimerAPI:
    """Test safety timer API endpoints."""

    LIST_URL = '/api/v1/safety-timers/'
    CREATE_URL = '/api/v1/safety-timers/create/'

    def test_create_timer(self, auth_client, safety_timer_data):
        response = auth_client.post(self.CREATE_URL, safety_timer_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'active'
        assert response.data['destination_address'] == 'Osh, Kyrgyzstan'
        assert response.data['auto_trigger_alert'] is False

    def test_create_timer_with_auto_sos(self, auth_client):
        response = auth_client.post(self.CREATE_URL, {
            'destination_latitude': 42.87,
            'destination_longitude': 74.57,
            'destination_address': 'Bishkek',
            'estimated_arrival_minutes': 60,
            'auto_trigger_alert': True,
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['auto_trigger_alert'] is True

    def test_create_timer_invalid_time(self, auth_client):
        """Must have positive estimated_arrival_minutes."""
        response = auth_client.post(self.CREATE_URL, {
            'destination_latitude': 42.87,
            'destination_longitude': 74.57,
            'destination_address': 'Test',
            'estimated_arrival_minutes': 0,
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_timer_unauthenticated(self, api_client, safety_timer_data):
        response = api_client.post(self.CREATE_URL, safety_timer_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_timers(self, auth_client, user, safety_timer_data):
        SafetyTimer.objects.create(user=user, **safety_timer_data)
        response = auth_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_confirm_arrival(self, auth_client, user, safety_timer_data):
        timer = SafetyTimer.objects.create(user=user, **safety_timer_data)
        confirm_url = f'/api/v1/safety-timers/{timer.id}/confirm/'
        response = auth_client.post(confirm_url)
        assert response.status_code == status.HTTP_200_OK
        timer.refresh_from_db()
        assert timer.status == 'arrived'

    def test_cancel_timer_api(self, auth_client, user, safety_timer_data):
        timer = SafetyTimer.objects.create(user=user, **safety_timer_data)
        cancel_url = f'/api/v1/safety-timers/{timer.id}/cancel/'
        response = auth_client.post(cancel_url)
        assert response.status_code == status.HTTP_200_OK
        timer.refresh_from_db()
        assert timer.status == 'cancelled'

    def test_confirm_other_users_timer(self, auth_client, second_user, safety_timer_data):
        timer = SafetyTimer.objects.create(user=second_user, **safety_timer_data)
        confirm_url = f'/api/v1/safety-timers/{timer.id}/confirm/'
        response = auth_client.post(confirm_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_confirm_already_arrived(self, auth_client, user):
        timer = SafetyTimer.objects.create(
            user=user, destination_latitude=42.0, destination_longitude=74.0,
            destination_address='Test', estimated_arrival_at=timezone.now() + timedelta(hours=1),
            status=SafetyTimer.Status.ARRIVED,
        )
        confirm_url = f'/api/v1/safety-timers/{timer.id}/confirm/'
        response = auth_client.post(confirm_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
