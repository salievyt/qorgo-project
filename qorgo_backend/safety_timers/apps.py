from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SafetyTimersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'safety_timers'
    verbose_name = _('Safety Timers')
