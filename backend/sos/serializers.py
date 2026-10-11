from rest_framework import serializers
from .models import Alert, EvidenceRecording
from accounts.serializers import UserBasicSerializer


class CreateAlertSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    address = serializers.CharField(required=False, allow_blank=True)
    trigger_method = serializers.ChoiceField(
        choices=Alert.TriggerMethod.choices,
        default=Alert.TriggerMethod.SOS_BUTTON,
    )
    battery_level = serializers.FloatField(default=0)


class AlertSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = (
            'id', 'user', 'started_at', 'resolved_at', 'resolved_by',
            'notified_contacts', 'family_notified', 'emergency_services_notified',
        )


class AlertListSerializer(serializers.ModelSerializer):
    """Minimal alert info for list view."""
    class Meta:
        model = Alert
        fields = (
            'id', 'status', 'trigger_method', 'latitude', 'longitude',
            'address', 'battery_level', 'started_at', 'resolved_at',
        )


class ResolveAlertSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['resolved', 'false_alarm'],
        default='resolved',
    )


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceRecording
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')
