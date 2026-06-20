from rest_framework import serializers
from .models import AnalyticsEvent, DailyReport


class AnalyticsEventSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = AnalyticsEvent
        fields = ('id', 'user', 'user_phone', 'event_name', 'session_id', 'parameters', 'timestamp')
        read_only_fields = ('id', 'timestamp')


class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        fields = '__all__'
