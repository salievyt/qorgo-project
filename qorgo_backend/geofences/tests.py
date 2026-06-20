"""
Tests for geofences app — Safe zone CRUD, geofence events.
"""
import pytest
from rest_framework import status
from geofences.models import Geofence, GeofenceEvent


class TestGeofenceModel:
    """Test Geofence model."""

    def test_create_geofence(self, user, geofence_data):
        geofence = Geofence.objects.create(
            user=user,
            **geofence_data,
        )
        assert geofence.name == 'Home'
        assert geofence.zone_type == 'home'
        assert geofence.radius == 100.0
        assert geofence.is_active is True
        assert 'Home' in str(geofence)

    def test_inactive_geofence(self, user, geofence_data):
        geofence = Geofence.objects.create(user=user, **geofence_data, is_active=False)
        assert geofence.is_active is False


class TestGeofenceEvent:
    """Test GeofenceEvent model."""

    def test_create_event(self, user, geofence_data):
        geofence = Geofence.objects.create(user=user, **geofence_data)
        event = GeofenceEvent.objects.create(
            geofence=geofence,
            user=user,
            event_type=GeofenceEvent.EventType.ENTRY,
            latitude=42.8746,
            longitude=74.5698,
        )
        assert event.event_type == 'entry'
        assert str(event).startswith('Entry')

    def test_exit_event(self, user, geofence_data):
        geofence = Geofence.objects.create(user=user, **geofence_data)
        event = GeofenceEvent.objects.create(
            geofence=geofence,
            user=user,
            event_type=GeofenceEvent.EventType.EXIT,
            latitude=42.8746,
            longitude=74.5698,
        )
        assert event.event_type == 'exit'
        assert str(event).startswith('Exit')

    def test_event_ordering(self, user, geofence_data):
        geofence = Geofence.objects.create(user=user, **geofence_data)
        e1 = GeofenceEvent.objects.create(
            geofence=geofence, user=user,
            event_type='entry', latitude=42.0, longitude=74.0,
        )
        e2 = GeofenceEvent.objects.create(
            geofence=geofence, user=user,
            event_type='exit', latitude=43.0, longitude=75.0,
        )
        events = GeofenceEvent.objects.all()
        assert events[0] == e2
        assert events[1] == e1


# ===== API Tests =====

class TestGeofenceAPI:
    """Test geofence API endpoints."""

    LIST_URL = '/api/v1/geofences/'

    def test_create_geofence(self, auth_client, geofence_data):
        response = auth_client.post(self.LIST_URL, geofence_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Home'
        assert response.data['zone_type'] == 'home'
        assert response.data['radius'] == 100.0

    def test_list_geofences(self, auth_client, user, geofence_data):
        Geofence.objects.create(user=user, **geofence_data)
        Geofence.objects.create(
            user=user, name='Work', zone_type='work',
            latitude=42.8, longitude=74.5, radius=200,
        )
        response = auth_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_other_user_geofences(self, auth_client, second_user, geofence_data):
        Geofence.objects.create(user=second_user, **geofence_data)
        response = auth_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_delete_geofence(self, auth_client, user, geofence_data):
        geofence = Geofence.objects.create(user=user, **geofence_data)
        detail_url = f'/api/v1/geofences/{geofence.id}/'
        response = auth_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        geofence.refresh_from_db()
        assert geofence.is_active is False  # Soft delete

    def test_update_geofence(self, auth_client, user, geofence_data):
        geofence = Geofence.objects.create(user=user, **geofence_data)
        detail_url = f'/api/v1/geofences/{geofence.id}/'
        response = auth_client.patch(detail_url, {'name': 'Updated Home'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Home'

    def test_unauthenticated_create(self, api_client, geofence_data):
        response = api_client.post(self.LIST_URL, geofence_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
