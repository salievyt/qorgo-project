from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count


@shared_task
def check_expired_safety_timers():
    """Check for expired safety timers and mark them as missed."""
    from safety_timers.models import SafetyTimer

    now = timezone.now()
    expired_timers = SafetyTimer.objects.filter(
        status=SafetyTimer.Status.ACTIVE,
        estimated_arrival_at__lte=now,
    )

    for timer in expired_timers:
        timer.status = SafetyTimer.Status.MISSED
        timer.save(update_fields=['status'])

        # If auto-trigger alert is enabled, create SOS alert
        if timer.auto_trigger_alert:
            from sos.models import Alert
            from common.services import generate_map_link

            Alert.objects.create(
                user=timer.user,
                status=Alert.Status.ACTIVE,
                trigger_method=Alert.TriggerMethod.SAFETY_TIMER,
                latitude=timer.destination_latitude,
                longitude=timer.destination_longitude,
                address=timer.destination_address,
                map_link=generate_map_link(timer.destination_latitude, timer.destination_longitude),
                battery_level=0,
            )

    return f'Checked {expired_timers.count()} expired timers'


@shared_task
def mark_stale_locations():
    """Mark locations as stale if no update received in 2 minutes."""
    from location.models import ActiveLocation

    stale_threshold = timezone.now() - timedelta(seconds=120)
    stale = ActiveLocation.objects.filter(
        last_updated__lt=stale_threshold,
        is_stale=False,
    )
    count = stale.update(is_stale=True)
    return f'Marked {count} locations as stale'


@shared_task
def cleanup_old_location_history():
    """Delete location history older than retention period (7 days for free, 365 for premium)."""
    from location.models import LocationUpdate
    from accounts.models import User

    # Free users: 7 days
    free_cutoff = timezone.now() - timedelta(days=7)
    LocationUpdate.objects.filter(
        user__is_premium=False,
        timestamp__lt=free_cutoff,
    ).delete()

    # Premium users: 365 days
    premium_cutoff = timezone.now() - timedelta(days=365)
    LocationUpdate.objects.filter(
        user__is_premium=True,
        timestamp__lt=premium_cutoff,
    ).delete()

    return 'Old location history cleaned up'


@shared_task
def cleanup_expired_evidence():
    """Delete evidence files older than retention period."""
    from sos.models import EvidenceRecording

    cutoff = timezone.now() - timedelta(days=365)
    expired = EvidenceRecording.objects.filter(created_at__lt=cutoff)
    count = expired.count()
    expired.delete()
    return f'Deleted {count} expired evidence files'


@shared_task
def expire_subscriptions():
    """Mark subscriptions that have expired as expired."""
    from subscriptions.models import Subscription

    now = timezone.now()
    expired = Subscription.objects.filter(
        status__in=['active', 'trial'],
        expires_at__lte=now,
    )

    for sub in expired:
        sub.status = Subscription.Status.EXPIRED
        sub.save(update_fields=['status'])

        # Update user premium status
        user = sub.user
        has_other_active = Subscription.objects.filter(
            user=user,
            status='active',
        ).exists()
        if not has_other_active:
            user.is_premium = False
            user.save(update_fields=['is_premium'])

    return f'Expired {expired.count()} subscriptions'


@shared_task
def generate_daily_report():
    """Generate daily analytics report."""
    from analytics.models import DailyReport
    from accounts.models import User
    from sos.models import Alert
    from families.models import Family
    from safety_timers.models import SafetyTimer

    today = timezone.now().date()

    report, created = DailyReport.objects.get_or_create(date=today)
    report.total_users = User.objects.filter(is_deleted=False).count()
    report.new_users = User.objects.filter(date_joined__date=today).count()
    report.active_users = User.objects.filter(last_active_at__date=today).count()
    report.premium_users = User.objects.filter(is_premium=True).count()
    report.sos_alerts_count = Alert.objects.filter(started_at__date=today).count()
    report.active_alerts_count = Alert.objects.filter(status='active').count()
    report.families_created = Family.objects.filter(created_at__date=today).count()
    report.safety_timers_created = SafetyTimer.objects.filter(started_at__date=today).count()
    report.save()

    return f'Report for {today} generated'
