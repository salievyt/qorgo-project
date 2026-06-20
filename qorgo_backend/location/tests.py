"""
Tests for location app — Location updates, history, active location.
"""
import pytest
from rest_framework import status
from location.models import LocationUpdate, ActiveLocation
from accounts.models import User


class TestLocationModel:
    """Test LocationUpdate model."""

    def test_create_location_update(self, user, bishkek_location):
        loc = LocationUpdate.objects.create(
            user=user,
            **bishkek_location,
        )
        assert loc.latitude == bishkek_location['latitude']
        assert loc.longitude == bishkek_location['longitude']
        assert loc.battery_level == 85.0
        assert loc.is_background is False

    def test_location_ordering(self, user):
        loc1 = LocationUpdate.objects.create(user=user, latitude=42.0, longitude=74.0)
        loc2 = LocationUpdate.objects.create(user=user, latitude=43.0, longitude=75.0)
        locations = LocationUpdate.objects.all()
        assert locations[0] == loc2  # Most recent first
        assert locations[1] == loc1

    def test_str_repr(self, user):
        loc = LocationUpdate.objects.create(user=user, latitude=42.8746, longitude=74.5698)
        assert str(user) in str(loc)
        assert '42.8746' in str(loc)


class TestActiveLocationModel:
    """Test ActiveLocation model (OneToOne with User)."""

    def test_create_active_location(self, user, bishkek_location):
        active = ActiveLocation.objects.create(
            user=user,
            latitude=bishkek_location['latitude'],
            longitude=bishkek_location['longitude'],
            speed=0.5,
            battery_level=85.0,
        )
        assert active.is_stale is False
        assert active.speed == 0.5

    def test_one_to_one_constraint(self, user, bishkek_location):
        ActiveLocation.objects.create(user=user, latitude=42.0, longitude=74.0)
        with pytest.raises(Exception):
            ActiveLocation.objects.create(user=user, latitude=43.0, longitude=75.0)

    def test_update_or_create(self, user, bishkek_location):
        active, created = ActiveLocation.objects.update_or_create(
            user=user,
            defaults={
                'latitude': 42.0,
                'longitude': 74.0,
                'speed': 2.0,
            },
        )
        assert created is True

        active, created = ActiveLocation.objects.update_or_create(
            user=user,
            defaults={
                'latitude': 43.0,
                'longitude': 75.0,
                'speed': 5.0,
            },
        )
        assert created is False
        assert active.latitude == 43.0
        assert active.speed == 5.0


# ===== API Tests =====

class TestLocationAPI:
    """Test location API endpoints."""

    UPDATE_URL = '/api/v1/location/update/'
    MY_LOCATION_URL = '/api/v1/location/me/'
    HISTORY_URL = '/api/v1/location/history/'

    def test_update_location(self, auth_client, user, bishkek_location):
        response = auth_client.post(self.UPDATE_URL, bishkek_location, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

        # Verify saved in DB
        assert LocationUpdate.objects.filter(user=user).count() == 1
        assert ActiveLocation.objects.filter(user=user).count() == 1

    def test_update_location_minimal(self, auth_client):
        """Update with just lat/lng."""
        response = auth_client.post(self.UPDATE_URL, {
            'latitude': 42.8746,
            'longitude': 74.5698,
        }, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_update_location_unauthenticated(self, api_client):
        response = api_client.post(self.UPDATE_URL, {
            'latitude': 42.0, 'longitude': 74.0,
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_my_location(self, auth_client, user, bishkek_location):
        ActiveLocation.objects.create(
            user=user,
            latitude=bishkek_location['latitude'],
            longitude=bishkek_location['longitude'],
            speed=0.5,
            battery_level=85,
        )
        response = auth_client.get(self.MY_LOCATION_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['latitude'] == bishkek_location['latitude']
        assert response.data['battery_level'] == 85.0

    def test_get_my_location_none(self, auth_client):
        """Should return None if no location recorded."""
        response = auth_client.get(self.MY_LOCATION_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['location'] is None

    def test_location_history(self, auth_client, user):
        for i in range(5):
            LocationUpdate.objects.create(
                user=user,
                latitude=42.0 + i * 0.01,
                longitude=74.0 + i * 0.01,
            )
        response = auth_client.get(self.HISTORY_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5

    def test_location_history_other_user(self, auth_client, second_user):
        """User should only see their own history."""
        LocationUpdate.objects.create(user=second_user, latitude=42.0, longitude=74.0)
        response = auth_client.get(self.HISTORY_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_family_locations(self, auth_client, user, second_user):
        """Family locations view."""
        from families.models import Family, FamilyMembership
        family = Family.objects.create(
            name='Test Family', created_by=user, invite_code='LOCS',
        )
        FamilyMembership.objects.create(
            family=family, user=user,
            role=FamilyMembership.Role.CREATOR, invited_by=user,
        )
        FamilyMembership.objects.create(
            family=family, user=second_user,
            role=FamilyMembership.Role.FRIEND, invited_by=user,
        )
        ActiveLocation.objects.create(
            user=second_user, latitude=42.0, longitude=74.0, speed=2.0,
        )
        response = auth_client.get(f'/api/v1/families/{family.id}/locations/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # Other member's location
