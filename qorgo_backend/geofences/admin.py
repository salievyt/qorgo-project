from django.contrib import admin
from .models import Geofence, GeofenceEvent


@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone_type', 'user', 'is_active', 'radius', 'created_at')
    list_filter = ('zone_type', 'is_active')
    search_fields = ('name', 'user__phone_number')


@admin.register(GeofenceEvent)
class GeofenceEventAdmin(admin.ModelAdmin):
    list_display = ('geofence', 'user', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
