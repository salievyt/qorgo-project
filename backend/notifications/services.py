import json
import logging
from typing import Optional
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


def _get_firebase_app():
    """Get or initialize Firebase Admin SDK."""
    try:
        import firebase_admin
        from firebase_admin import credentials
        if not firebase_admin._apps:
            if settings.FIREBASE_CREDENTIALS_PATH:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_DATABASE_URL,
                })
            else:
                # Use default credentials (GOOGLE_APPLICATION_CREDENTIALS env var)
                firebase_admin.initialize_app()
        return firebase_admin
    except ImportError:
        logger.warning('firebase-admin not installed. Push notifications disabled.')
        return None
    except Exception as e:
        logger.error(f'Firebase initialization error: {e}')
        return None


def send_push_notification(
    user,
    title: str,
    body: str,
    data: Optional[dict] = None,
    priority: str = 'normal',
) -> bool:
    """
    Send push notification to a user via Firebase Cloud Messaging.
    Falls back to console logging if Firebase is not configured.
    """
    if not user.fcm_tokens:
        logger.info(f'[Push] No FCM tokens for {user}. Skipping.')
        return False

    try:
        firebase_app = _get_firebase_app()
        if firebase_app:
            from firebase_admin import messaging

            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={k: str(v) for k, v in (data or {}).items()},
                tokens=user.fcm_tokens,
                android=messaging.AndroidConfig(
                    priority='high' if priority == 'critical' else 'normal',
                    notification=messaging.AndroidNotification(
                        channel_id='critical_alerts' if priority == 'critical' else 'general_notifications',
                        priority='high' if priority == 'critical' else 'default',
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(title=title, body=body),
                            sound='alarm.caf' if priority == 'critical' else 'default',
                            badge=1,
                            content_available=True,
                        ),
                    ),
                ),
            )

            response = messaging.send_each_for_multicast(message)

            # Clean up invalid tokens
            if response.failure_count > 0:
                invalid_tokens = []
                for idx, resp in enumerate(response.responses):
                    if not resp.success and resp.error.code in [
                        'messaging/invalid-registration-token',
                        'messaging/registration-token-not-registered',
                    ]:
                        invalid_tokens.append(user.fcm_tokens[idx])

                if invalid_tokens:
                    user.fcm_tokens = [t for t in user.fcm_tokens if t not in invalid_tokens]
                    user.save(update_fields=['fcm_tokens'])

            return response.success_count > 0
        else:
            # Fallback: log notification
            logger.info(f'[Push] To: {user.phone_number}')
            logger.info(f'[Push] Title: {title}')
            logger.info(f'[Push] Body: {body}')
            logger.info(f'[Push] Data: {data}')
            return True

    except Exception as e:
        logger.error(f'Push notification error for {user}: {e}')
        # Fallback: just log it
        logger.info(f'[Push] (fallback) To: {user.phone_number}, Title: {title}')
        return False


def send_sos_alert_to_contacts(alert, user, contacts):
    """Send SOS alert to all emergency contacts."""
    notified = []
    for contact in contacts:
        success = send_push_notification(
            contact.contact if hasattr(contact, 'contact') else contact,
            '🚨 SOS Alert!',
            f'{user.first_name} {user.last_name} needs urgent help!',
            {
                'type': 'sos_alert',
                'alert_id': str(alert.id),
                'user_id': str(user.id),
                'latitude': str(alert.latitude),
                'longitude': str(alert.longitude),
                'map_link': alert.map_link,
            },
            priority='critical',
        )
        if success:
            notified.append(str(contact.id))
    return notified


def notify_family_members(family, exclude_user, title, body, data=None):
    """Send notification to all family members except one."""
    from families.models import FamilyMembership
    members = FamilyMembership.objects.filter(family=family).exclude(user=exclude_user)
    for membership in members:
        send_push_notification(
            membership.user,
            title,
            body,
            data or {},
        )


def send_location_broadcast(user, latitude, longitude, speed, battery_level):
    """Send location update notification to family members (used as fallback if WebSocket not connected)."""
    from families.models import Family
    from location.models import ActiveLocation

    families = Family.objects.filter(members=user)
    for family in families:
        members = family.members.exclude(id=user.id)
        for member in members:
            send_push_notification(
                member,
                '📍 Location Update',
                f'{user.first_name} {user.last_name} updated their location',
                {
                    'type': 'location_update',
                    'user_id': str(user.id),
                    'latitude': str(latitude),
                    'longitude': str(longitude),
                    'speed': str(speed),
                    'battery_level': str(battery_level),
                },
            )

    # Update active location
    ActiveLocation.objects.update_or_create(
        user=user,
        defaults={
            'latitude': latitude,
            'longitude': longitude,
            'speed': speed,
            'battery_level': battery_level,
            'is_stale': False,
        },
    )
