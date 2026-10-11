import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class SubscriptionPlan(models.Model):
    """Defines available subscription plans and their features."""
    class PlanType(models.TextChoices):
        FREE = 'free', _('Free')
        PREMIUM_MONTHLY = 'premium_monthly', _('Premium Monthly')
        PREMIUM_YEARLY = 'premium_yearly', _('Premium Yearly')
        FAMILY_MONTHLY = 'family_monthly', _('Family Monthly')
        FAMILY_YEARLY = 'family_yearly', _('Family Yearly')
        CORPORATE = 'corporate', _('Corporate')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_type = models.CharField(max_length=30, choices=PlanType.choices, unique=True, verbose_name=_('Plan type'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Price (USD)'))
    price_som = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Price (KGS)'))

    # Features
    max_family_members = models.PositiveSmallIntegerField(default=5, verbose_name=_('Max family members'))
    history_retention_days = models.PositiveIntegerField(default=7, verbose_name=_('History retention (days)'))
    ai_safety_analysis = models.BooleanField(default=False, verbose_name=_('AI safety analysis'))
    video_recording = models.BooleanField(default=False, verbose_name=_('Video recording'))
    cloud_backup = models.BooleanField(default=False, verbose_name=_('Cloud backup'))
    priority_notifications = models.BooleanField(default=False, verbose_name=_('Priority notifications'))

    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Subscription plan')
        verbose_name_plural = _('Subscription plans')

    def __str__(self):
        return f'{self.name} — ${self.price_usd}/mo'


class Subscription(models.Model):
    """User subscription record."""
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        CANCELED = 'canceled', _('Canceled')
        EXPIRED = 'expired', _('Expired')
        TRIAL = 'trial', _('Trial')

    class PaymentProvider(models.TextChoices):
        APPSTORE = 'appstore', _('App Store')
        PLAYSTORE = 'playstore', _('Google Play')
        ADMIN = 'admin', _('Admin')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='subscriptions', verbose_name=_('User'),
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, verbose_name=_('Plan'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL, verbose_name=_('Status'))
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Started at'))
    expires_at = models.DateTimeField(verbose_name=_('Expires at'))
    canceled_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Canceled at'))
    auto_renew = models.BooleanField(default=True, verbose_name=_('Auto renew'))
    payment_provider = models.CharField(
        max_length=20, choices=PaymentProvider.choices,
        default=PaymentProvider.ADMIN, verbose_name=_('Payment provider'),
    )
    payment_provider_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Payment provider ID'))

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} — {self.plan.name} ({self.status})'
