import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class LocationUpdate(models.Model):
    """Individual location update record for history."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='location_updates', verbose_name=_('User'),
    )
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    accuracy = models.FloatField(default=0, verbose_name=_('Accuracy (m)'))
    altitude = models.FloatField(blank=True, null=True, verbose_name=_('Altitude (m)'))
    speed = models.FloatField(default=0, verbose_name=_('Speed (m/s)'))
    heading = models.FloatField(default=0, verbose_name=_('Heading (°)'))
    battery_level = models.FloatField(default=100, verbose_name=_('Battery level'))
    is_background = models.BooleanField(default=False, verbose_name=_('Background update'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))

    class Meta:
        verbose_name = _('Location update')
        verbose_name_plural = _('Location updates')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f'{self.user} @ ({self.latitude}, {self.longitude})'


class ActiveLocation(models.Model):
    """Current active location for each user (used by family members)."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        primary_key=True, related_name='active_location',
        verbose_name=_('User'),
    )
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    accuracy = models.FloatField(default=0, verbose_name=_('Accuracy (m)'))
    speed = models.FloatField(default=0, verbose_name=_('Speed (m/s)'))
    battery_level = models.FloatField(default=100, verbose_name=_('Battery level'))
    is_stale = models.BooleanField(default=False, verbose_name=_('Is stale'))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_('Last updated'))

    class Meta:
        verbose_name = _('Active location')
        verbose_name_plural = _('Active locations')

    def __str__(self):
        return f'{self.user} — ({self.latitude}, {self.longitude})'
