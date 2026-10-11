from django.contrib import admin
from .models import Alert, EvidenceRecording


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'trigger_method', 'started_at', 'resolved_at')
    list_filter = ('status', 'trigger_method', 'started_at')
    search_fields = ('user__phone_number', 'address')
    raw_id_fields = ('user', 'resolved_by')


@admin.register(EvidenceRecording)
class EvidenceRecordingAdmin(admin.ModelAdmin):
    list_display = ('id', 'alert', 'evidence_type', 'user', 'created_at')
    list_filter = ('evidence_type',)
