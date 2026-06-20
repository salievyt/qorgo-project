import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class SafetyTimer(models.Model):
    """'I should arrive by' safety timer."""
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        ARRIVED = 'arrived', _('Arrived')
        MISSED = 'missed', _('Missed')
        CANCELLED = 'cancelled', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='safety_timers', verbose_name=_('User'),
    )
    destination_latitude = models.FloatField(verbose_name=_('Destination latitude'))
    destination_longitude = models.FloatField(verbose_name=_('Destination longitude'))
    destination_address = models.TextField(verbose_name=_('Destination address'))
    estimated_arrival_at = models.DateTimeField(verbose_name=_('Estimated arrival'))
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Started at'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name=_('Status'))
    auto_trigger_alert = models.BooleanField(default=False, verbose_name=_('Auto-trigger SOS'))
    notified_contacts = models.JSONField(default=list, blank=True, verbose_name=_('Notified contacts'))

    class Meta:
        verbose_name = _('Safety timer')
        verbose_name_plural = _('Safety timers')
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} → {self.destination_address} ({self.status})'
