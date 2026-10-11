import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Geofence(models.Model):
    """Safe zone / geofence for location-based notifications."""
    class GeofenceType(models.TextChoices):
        HOME = 'home', _('Home')
        SCHOOL = 'school', _('School')
        UNIVERSITY = 'university', _('University')
        WORK = 'work', _('Work')
        CUSTOM = 'custom', _('Custom')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='geofences', verbose_name=_('User'),
    )
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    zone_type = models.CharField(
        max_length=20, choices=GeofenceType.choices,
        default=GeofenceType.CUSTOM, db_column='type',
        verbose_name=_('Zone type'),
    )
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    radius = models.FloatField(verbose_name=_('Radius (m)'))  # in meters
    address = models.TextField(blank=True, verbose_name=_('Address'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    notify_on_entry = models.BooleanField(default=True, verbose_name=_('Notify on entry'))
    notify_on_exit = models.BooleanField(default=True, verbose_name=_('Notify on exit'))
    notify_family = models.BooleanField(default=True, verbose_name=_('Notify family'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    # Families to notify (0=all, specific families listed)
    family_notification_list = models.ManyToManyField(
        'families.Family', blank=True,
        verbose_name=_('Families to notify'),
    )

    class Meta:
        verbose_name = _('Geofence')
        verbose_name_plural = _('Geofences')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_zone_type_display()})'


class GeofenceEvent(models.Model):
    """Record of entry/exit events for geofences."""
    class EventType(models.TextChoices):
        ENTRY = 'entry', _('Entry')
        EXIT = 'exit', _('Exit')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geofence = models.ForeignKey(Geofence, on_delete=models.CASCADE, related_name='events', verbose_name=_('Geofence'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='geofence_events', verbose_name=_('User'),
    )
    event_type = models.CharField(max_length=10, choices=EventType.choices, verbose_name=_('Event type'))
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))
    notified_users = models.JSONField(default=list, blank=True, verbose_name=_('Notified users'))

    class Meta:
        verbose_name = _('Geofence event')
        verbose_name_plural = _('Geofence events')
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.get_event_type_display()} — {self.geofence.name} ({self.timestamp})'
