import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AnalyticsEvent(models.Model):
    """Track application events for analytics."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='analytics_events', verbose_name=_('User'),
    )
    event_name = models.CharField(max_length=255, verbose_name=_('Event name'))
    session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Session ID'))
    parameters = models.JSONField(default=dict, blank=True, verbose_name=_('Parameters'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP address'))
    user_agent = models.TextField(blank=True, verbose_name=_('User agent'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))

    class Meta:
        verbose_name = _('Analytics event')
        verbose_name_plural = _('Analytics events')
        indexes = [
            models.Index(fields=['event_name', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f'{self.event_name} — {self.timestamp}'


class DailyReport(models.Model):
    """Daily summary report for admin dashboard."""
    date = models.DateField(unique=True, verbose_name=_('Date'))
    total_users = models.PositiveIntegerField(default=0, verbose_name=_('Total users'))
    new_users = models.PositiveIntegerField(default=0, verbose_name=_('New users'))
    active_users = models.PositiveIntegerField(default=0, verbose_name=_('Active users'))
    premium_users = models.PositiveIntegerField(default=0, verbose_name=_('Premium users'))
    sos_alerts_count = models.PositiveIntegerField(default=0, verbose_name=_('SOS alerts'))
    active_alerts_count = models.PositiveIntegerField(default=0, verbose_name=_('Active alerts'))
    families_created = models.PositiveIntegerField(default=0, verbose_name=_('Families created'))
    safety_timers_created = models.PositiveIntegerField(default=0, verbose_name=_('Safety timers'))
    total_revenue_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Revenue (USD)'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Daily report')
        verbose_name_plural = _('Daily reports')

    def __str__(self):
        return f'Report — {self.date}'
