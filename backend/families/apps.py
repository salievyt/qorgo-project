from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FamiliesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'families'
    verbose_name = _('Family Groups')
