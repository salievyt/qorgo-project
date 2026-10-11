from datetime import datetime, timezone
from types import SimpleNamespace
from safety.services import alert_message


def test_sos_message_has_openstreetmap_marker_even_at_zero_latitude():
    alert = SimpleNamespace(owner=SimpleNamespace(first_name='Qorgo', email='test@example.com'),
        reason='sos', latitude=0.0, longitude=-1.0,
        location_at=datetime(2026, 1, 1, tzinfo=timezone.utc), location_accuracy=15)
    message = alert_message(alert)
    assert 'https://www.openstreetmap.org/?mlat=0.0&mlon=-1.0#map=16/0.0/-1.0' in message
    assert 'google.com' not in message


def test_sos_without_location_does_not_invent_a_map_point():
    alert = SimpleNamespace(owner=SimpleNamespace(first_name='Qorgo', email='test@example.com'), reason='sos', latitude=None)
    message = alert_message(alert)
    assert 'Геопозиция недоступна.' in message
    assert 'openstreetmap.org' not in message
