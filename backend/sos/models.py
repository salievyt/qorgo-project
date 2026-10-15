import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Alert(models.Model):
    """SOS alert / emergency activation."""
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        RESOLVED = 'resolved', _('Resolved')
        FALSE_ALARM = 'false_alarm', _('False alarm')
        EXPIRED = 'expired', _('Expired')

    class TriggerMethod(models.TextChoices):
        SOS_BUTTON = 'sos_button', _('SOS Button')
        WIDGET = 'widget', _('Widget')
        POWER_BUTTON = 'power_button', _('Power Button')
        SHAKE = 'shake', _('Shake')
        SAFETY_TIMER = 'safety_timer', _('Safety Timer')
        AI_SAFETY = 'safety_ai', _('AI Safety')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='alerts', verbose_name=_('User'),
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name=_('Status'))
    trigger_method = models.CharField(max_length=20, choices=TriggerMethod.choices, default=TriggerMethod.SOS_BUTTON, verbose_name=_('Trigger method'))
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Address'))
    map_link = models.URLField(max_length=500, blank=True, verbose_name=_('Map link'))
    battery_level = models.FloatField(default=0, verbose_name=_('Battery level'))
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Started at'))
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Resolved at'))
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_alerts', verbose_name=_('Resolved by'),
    )
    assigned_operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_incidents', verbose_name=_('Assigned operator'),
    )
    assigned_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Assigned at'))
    operator_note = models.TextField(blank=True, verbose_name=_('Operator note'))
    notified_contacts = models.JSONField(default=list, blank=True, verbose_name=_('Notified contacts'))
    family_notified = models.BooleanField(default=False, verbose_name=_('Family notified'))
    emergency_services_notified = models.BooleanField(default=False, verbose_name=_('Emergency services notified'))

    class Meta:
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')
        ordering = ['-started_at']

    def __str__(self):
        return f'SOS {self.status} — {self.user} ({self.started_at})'


class EvidenceRecording(models.Model):
    """Audio/video/photo evidence recorded during SOS alert."""
    class EvidenceType(models.TextChoices):
        AUDIO = 'audio', _('Audio')
        VIDEO_FRONT = 'video_front', _('Video (Front Camera)')
        VIDEO_BACK = 'video_back', _('Video (Back Camera)')
        PHOTO = 'photo', _('Photo')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='evidence', verbose_name=_('Alert'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='evidence_recordings', verbose_name=_('User'),
    )
    evidence_type = models.CharField(max_length=20, choices=EvidenceType.choices, verbose_name=_('Type'))
    file = models.FileField(upload_to='evidence/%Y/%m/%d/', verbose_name=_('File'))
    duration_seconds = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Duration (s)'))
    file_size_bytes = models.PositiveBigIntegerField(verbose_name=_('File size'))
    mime_type = models.CharField(max_length=100, verbose_name=_('MIME type'))
    is_encrypted = models.BooleanField(default=True, verbose_name=_('Encrypted'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Evidence recording')
        verbose_name_plural = _('Evidence recordings')

    def __str__(self):
        return f'{self.evidence_type} — Alert {self.alert_id}'
