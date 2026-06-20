from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SOSConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sos'
    verbose_name = _('SOS Alerts')
