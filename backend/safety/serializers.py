import re
from rest_framework import serializers
from .models import Contact, Alert, Delivery, Journey

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone', 'email', 'relationship']
    def validate_phone(self, value):
        value = re.sub(r'[\s()\-]', '', value)
        if not re.fullmatch(r'\+[1-9]\d{7,14}', value):
            raise serializers.ValidationError('Введите международный номер, например +996…')
        return value
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Укажите имя.')
        return value.strip()

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['name', 'status', 'channel', 'attempts']

class AlertSerializer(serializers.ModelSerializer):
    deliveries = DeliverySerializer(many=True, read_only=True)
    class Meta:
        model = Alert
        fields = ['id', 'request_id', 'created_at', 'reason', 'latitude', 'longitude', 'location_accuracy', 'location_at', 'resolved_at', 'deliveries']

class AlertInputSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    latitude = serializers.FloatField(min_value=-90, max_value=90, allow_null=True, required=False)
    longitude = serializers.FloatField(min_value=-180, max_value=180, allow_null=True, required=False)
    location_accuracy = serializers.FloatField(min_value=0, allow_null=True, required=False)
    location_at = serializers.DateTimeField(allow_null=True, required=False)
    def validate(self, attrs):
        if (attrs.get('latitude') is None) != (attrs.get('longitude') is None):
            raise serializers.ValidationError('Both coordinates are required together.')
        return attrs

class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ['id', 'destination', 'deadline', 'state', 'created_at', 'alert']
        read_only_fields = ['state', 'created_at', 'alert']
