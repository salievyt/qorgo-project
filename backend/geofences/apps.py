from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GeofencesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'geofences'
    verbose_name = _('Safe Zones')
