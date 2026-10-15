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
    assigned_operator_name = serializers.SerializerMethodField()

    def get_assigned_operator_name(self, alert):
        operator = alert.assigned_operator
        if not operator:
            return ''
        return operator.get_full_name().strip() or operator.phone_number or 'Оператор QORGO'

    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = (
            'id', 'user', 'started_at', 'resolved_at', 'resolved_by',
            'notified_contacts', 'family_notified', 'emergency_services_notified',
        )


class OperatorIncidentSerializer(AlertSerializer):
    """Incident details exposed only to authorised response staff."""

    class Meta(AlertSerializer.Meta):
        fields = '__all__'


class OperatorIncidentUpdateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    status = serializers.ChoiceField(
        choices=[Alert.Status.RESOLVED, Alert.Status.FALSE_ALARM], required=False,
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
