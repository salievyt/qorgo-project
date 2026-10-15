from django.contrib import admin
from qorgo.admin import QorgoAdminLabelsMixin
from .models import AnalyticsEvent, DailyReport


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('event_name', 'user', 'session_id', 'timestamp')
    list_filter = ('event_name', 'timestamp')
    search_fields = ('user__phone_number',)


@admin.register(DailyReport)
class DailyReportAdmin(QorgoAdminLabelsMixin, admin.ModelAdmin):
    list_display = ('date', 'total_users', 'active_users', 'sos_alerts_count', 'created_at')
    list_filter = ('date',)
