"""Distinct enum names for models sharing status and role field names."""
from families.models import FamilyMembership
from safety_timers.models import SafetyTimer
from sos.models import Alert
from subscriptions.models import Subscription

SOS_STATUS_CHOICES = Alert.Status.choices
SAFETY_TIMER_STATUS_CHOICES = SafetyTimer.Status.choices
SUBSCRIPTION_STATUS_CHOICES = Subscription.Status.choices
FAMILY_ROLE_CHOICES = FamilyMembership.Role.choices
