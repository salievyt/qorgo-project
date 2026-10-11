from django.contrib import admin
from .models import LocationUpdate, ActiveLocation


@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'speed', 'battery_level', 'is_background', 'timestamp')
    list_filter = ('is_background', 'timestamp')
    search_fields = ('user__phone_number',)
    raw_id_fields = ('user',)


@admin.register(ActiveLocation)
class ActiveLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'speed', 'battery_level', 'is_stale', 'last_updated')
    list_filter = ('is_stale',)
