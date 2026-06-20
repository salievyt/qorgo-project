from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class QorgoAdminSite(AdminSite):
    """Custom admin site for Qorgo."""
    site_title = _('Qorgo Admin')
    site_header = _('Qorgo Safety Platform Administration')
    index_title = _('Dashboard')
    enable_nav_sidebar = True


# Replace default admin site
admin.site.__class__ = QorgoAdminSite
