from django.contrib import admin
from qorgo.admin import QorgoAdminLabelsMixin
from .models import Geofence, GeofenceEvent


@admin.register(Geofence)
class GeofenceAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('name', 'zone_type', 'user', 'is_active', 'radius', 'created_at')
    list_filter = ('zone_type', 'is_active')
    search_fields = ('name', 'user__phone_number')


@admin.register(GeofenceEvent)
class GeofenceEventAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('geofence', 'user', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
