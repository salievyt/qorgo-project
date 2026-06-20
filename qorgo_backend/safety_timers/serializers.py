from rest_framework import serializers
from .models import SafetyTimer


class SafetyTimerCreateSerializer(serializers.Serializer):
    destination_latitude = serializers.FloatField()
    destination_longitude = serializers.FloatField()
    destination_address = serializers.CharField()
    estimated_arrival_minutes = serializers.IntegerField(min_value=1, max_value=1440)  # Max 24 hours
    auto_trigger_alert = serializers.BooleanField(default=False)


class SafetyTimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyTimer
        fields = '__all__'
        read_only_fields = ('id', 'user', 'started_at', 'notified_contacts')


class ConfirmArrivalSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
