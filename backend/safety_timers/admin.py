from django.contrib import admin
from .models import SafetyTimer


@admin.register(SafetyTimer)
class SafetyTimerAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination_address', 'status', 'estimated_arrival_at', 'started_at')
    list_filter = ('status',)
    search_fields = ('user__phone_number', 'destination_address')
