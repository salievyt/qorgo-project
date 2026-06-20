"""
Tests for sos app — Alert creation, resolution, evidence recording.
"""
import pytest
from django.utils import timezone
from rest_framework import status
from sos.models import Alert, EvidenceRecording


class TestAlertModel:
    """Test Alert model."""

    def test_create_alert(self, user, bishkek_location):
        alert = Alert.objects.create(
            user=user,
            status=Alert.Status.ACTIVE,
            trigger_method=Alert.TriggerMethod.SOS_BUTTON,
            latitude=bishkek_location['latitude'],
            longitude=bishkek_location['longitude'],
            address='Chui Avenue, Bishkek',
            map_link='https://www.google.com/maps?q=42.8746,74.5698',
            battery_level=75.0,
        )
        assert alert.status == 'active'
        assert alert.trigger_method == 'sos_button'
        assert alert.family_notified is False
        assert alert.notified_contacts == []
        assert str(alert).startswith('SOS active')

    def test_default_status_active(self, user, bishkek_location):
        alert = Alert.objects.create(
            user=user,
            latitude=42.0, longitude=74.0,
        )
        assert alert.status == 'active'

    def test_resolve_alert(self, user, bishkek_location):
        alert = Alert.objects.create(
            user=user,
            latitude=42.0, longitude=74.0,
        )
        alert.status = Alert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.save()
        assert alert.status == 'resolved'

    def test_alert_ordering(self, user, bishkek_location):
        """Alerts should be ordered by -started_at (most recent first)."""
        alert1 = Alert.objects.create(user=user, latitude=42.0, longitude=74.0)
        alert2 = Alert.objects.create(user=user, latitude=43.0, longitude=75.0)
        alerts = Alert.objects.all()
        assert alerts[0] == alert2
        assert alerts[1] == alert1


class TestEvidenceModel:
    """Test EvidenceRecording model."""

    def test_create_evidence(self, user, bishkek_location):
        alert = Alert.objects.create(user=user, latitude=42.0, longitude=74.0)
        evidence = EvidenceRecording.objects.create(
            alert=alert,
            user=user,
            evidence_type=EvidenceRecording.EvidenceType.AUDIO,
            file='evidence/test/audio.mp3',
            file_size_bytes=1024,
            mime_type='audio/mp3',
        )
        assert evidence.evidence_type == 'audio'
        assert evidence.is_encrypted is True
        assert str(evidence) == f'audio — Alert {alert.id}'


# ===== API Tests =====

class TestAlertAPI:
    """Test SOS alert API endpoints."""

    CREATE_URL = '/api/v1/alerts/create/'
    LIST_URL = '/api/v1/alerts/'

    def test_create_alert(self, auth_client, user, sos_alert_data):
        response = auth_client.post(self.CREATE_URL, sos_alert_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'active'
        assert response.data['trigger_method'] == 'sos_button'
        assert response.data['user']['id'] == str(user.id)

    def test_create_alert_minimal_data(self, auth_client):
        """Alert should work with just lat/lng."""
        response = auth_client.post(self.CREATE_URL, {
            'latitude': 42.8746,
            'longitude': 74.5698,
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['trigger_method'] == 'sos_button'

    def test_create_alert_missing_location(self, auth_client):
        response = auth_client.post(self.CREATE_URL, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_alert_unauthenticated(self, api_client, sos_alert_data):
        response = api_client.post(self.CREATE_URL, sos_alert_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_user_alerts(self, auth_client, user, bishkek_location):
        Alert.objects.create(user=user, latitude=42.0, longitude=74.0)
        Alert.objects.create(user=user, latitude=43.0, longitude=75.0)
        response = auth_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_list_alerts_other_user(self, auth_client, second_user):
        """User should only see their own alerts."""
        Alert.objects.create(user=second_user, latitude=42.0, longitude=74.0)
        response = auth_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_resolve_alert(self, auth_client, user, bishkek_location):
        alert = Alert.objects.create(
            user=user,
            latitude=42.0, longitude=74.0,
            status=Alert.Status.ACTIVE,
        )
        resolve_url = f'/api/v1/alerts/{alert.id}/resolve/'
        response = auth_client.post(resolve_url, {'status': 'resolved'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'resolved'
        assert response.data['resolved_by']['id'] == str(user.id)
        assert response.data['resolved_at'] is not None

    def test_resolve_already_resolved(self, auth_client, user, bishkek_location):
        alert = Alert.objects.create(
            user=user,
            latitude=42.0, longitude=74.0,
            status=Alert.Status.RESOLVED,
            resolved_at=timezone.now(),
        )
        resolve_url = f'/api/v1/alerts/{alert.id}/resolve/'
        response = auth_client.post(resolve_url, {'status': 'resolved'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_resolve_other_users_alert(self, auth_client, second_user):
        alert = Alert.objects.create(
            user=second_user,
            latitude=42.0, longitude=74.0,
            status=Alert.Status.ACTIVE,
        )
        resolve_url = f'/api/v1/alerts/{alert.id}/resolve/'
        response = auth_client.post(resolve_url, {'status': 'resolved'}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_alert_detail(self, auth_client, user, bishkek_location):
        alert = Alert.objects.create(user=user, latitude=42.0, longitude=74.0)
        detail_url = f'/api/v1/alerts/{alert.id}/'
        response = auth_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(alert.id)
