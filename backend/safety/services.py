import base64
import json
import uuid
from datetime import timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from .models import Alert, Contact, Delivery, Journey
from common.services import generate_map_link

@transaction.atomic
def create_alert(owner, request_id, reason='sos', **location):
    alert, created = Alert.objects.get_or_create(owner=owner, request_id=request_id, defaults={'reason': reason, **location})
    if created:
        contacts = list(Contact.objects.filter(owner=owner).select_related('recipient'))
        registered = {email.lower() for email in get_user_model().objects.filter(
            email__in=[c.email.lower() for c in contacts if c.email], is_active=True, is_deleted=False,
        ).exclude(pk=owner.pk).values_list('email', flat=True)}
        Delivery.objects.bulk_create([
            Delivery(alert=alert, name=c.name, phone=c.phone,
                recipient=c.recipient if c.recipient and c.recipient.is_active and not c.recipient.is_deleted else None,
                email='' if c.recipient_id else c.email,
                channel='app' if (c.recipient and c.recipient.is_active and not c.recipient.is_deleted) or (not c.recipient_id and c.email.lower() in registered) else '',
                status='available' if (c.recipient and c.recipient.is_active and not c.recipient.is_deleted) or (not c.recipient_id and c.email.lower() in registered) else 'pending')
            for c in contacts
        ])
    return alert, created

@transaction.atomic
def finish_journey(owner, journey_id, action):
    journey = Journey.objects.select_for_update().get(owner=owner, id=journey_id)
    if journey.state != 'active':
        return journey
    if timezone.now() >= journey.deadline:
        expire_journey(journey)
    else:
        journey.state = action
        journey.save(update_fields=['state'])
    return journey

def expire_journey(journey):
    alert, _ = create_alert(journey.owner, uuid.uuid5(uuid.NAMESPACE_URL, f'qorgo/journey/{journey.id}'), reason='timer')
    journey.state = 'expired'
    journey.alert = alert
    journey.save(update_fields=['state', 'alert'])

def process_deadlines():
    for journey_id in Journey.objects.filter(state='active', deadline__lte=timezone.now()).values_list('id', flat=True):
        with transaction.atomic():
            journey = Journey.objects.select_for_update().get(id=journey_id)
            if journey.state == 'active' and journey.deadline <= timezone.now():
                expire_journey(journey)

def alert_message(alert):
    owner = alert.owner.first_name or alert.owner.email
    text = f'QORGO SOS: {owner} просит о помощи.'
    if alert.reason == 'timer':
        text += ' Прибытие не подтверждено вовремя.'
    if alert.latitude is not None:
        text += ' ' + generate_map_link(alert.latitude, alert.longitude)
        text += f' (геопозиция: {alert.location_at}, точность ±{alert.location_accuracy} м)'
    else:
        text += ' Геопозиция недоступна.'
    return text

def dispatch(delivery):
    sms_ready = all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_FROM])
    if sms_ready:
        auth = base64.b64encode(f'{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}'.encode()).decode()
        request = Request(
            f'https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json',
            data=urlencode({'To': delivery.phone, 'From': settings.TWILIO_FROM, 'Body': alert_message(delivery.alert)}).encode(),
            headers={'Authorization': f'Basic {auth}'}, method='POST',
        )
        with urlopen(request, timeout=10) as response:
            result = json.load(response)
        return 'sms', result['sid']
    if delivery.email and settings.EMAIL_HOST and settings.DEFAULT_FROM_EMAIL:
        result = send_mail('QORGO: сигнал SOS', alert_message(delivery.alert), settings.DEFAULT_FROM_EMAIL, [delivery.email], fail_silently=False)
        if result != 1:
            raise RuntimeError('Email was not accepted.')
        return 'email', ''
    return None

def process_deliveries():
    # Single worker only. Recover interrupted sends as "unknown" rather than
    # retrying a potentially accepted message and silently creating duplicates.
    Delivery.objects.filter(status='sending', updated_at__lt=timezone.now()-timedelta(minutes=2)).update(status='unknown')
    for delivery_id in Delivery.objects.filter(status__in=['pending', 'unconfigured'], alert__resolved_at__isnull=True).values_list('id', flat=True):
        claimed = Delivery.objects.filter(id=delivery_id, status__in=['pending', 'unconfigured']).update(status='sending', updated_at=timezone.now())
        if not claimed:
            continue
        delivery = Delivery.objects.select_related('alert__owner').get(id=delivery_id)
        try:
            result = dispatch(delivery)
            if result is None:
                delivery.status = 'unconfigured'
            else:
                delivery.channel, delivery.provider_id = result
                delivery.status = 'accepted'
                delivery.attempts += 1
        except Exception:
            # Network timeouts can occur after provider acceptance. Explicit
            # retry is required; no unbounded retry loop for SOS messages.
            delivery.status = 'unknown'
            delivery.attempts += 1
        Delivery.objects.filter(id=delivery.id, status='sending').update(
            status=delivery.status, channel=delivery.channel, provider_id=delivery.provider_id,
            attempts=delivery.attempts, updated_at=timezone.now(),
        )
