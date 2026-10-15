from drf_spectacular.utils import extend_schema_serializer
import re
from rest_framework import serializers
from .models import Contact, Alert, Delivery, Journey
from .phone_contacts import registered_user

@extend_schema_serializer(component_name='MobileContact')
class ContactSerializer(serializers.ModelSerializer):
    in_qorgo = serializers.SerializerMethodField()
    link_registered = serializers.BooleanField(write_only=True, required=False, default=False)
    def get_in_qorgo(self, instance):
        return bool(instance.recipient_id and instance.recipient.is_active and not instance.recipient.is_deleted)
    def validate(self, attrs):
        required = attrs.pop('link_registered', False)
        owner = self.context['request'].user
        phone = attrs.get('phone', self.instance.phone if self.instance else '')
        if owner.phone_number and str(owner.phone_number) == phone:
            raise serializers.ValidationError({'phone': 'Нельзя добавить себя в близкие.'})
        recipient = self.instance.recipient if self.instance and self.instance.phone == phone and self.instance.recipient_id else registered_user(phone, owner)
        if recipient and (not recipient.is_active or recipient.is_deleted):
            recipient = None
        if required and recipient is None:
            raise serializers.ValidationError({'phone': 'Аккаунт с этим номером больше не доступен. Найдите контакт заново.'})
        attrs['recipient'] = recipient
        return attrs

    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone', 'email', 'relationship', 'in_qorgo', 'link_registered']
    def validate_phone(self, value):
        value = re.sub(r'[\s()\-]', '', value)
        if not re.fullmatch(r'\+[1-9]\d{7,14}', value):
            raise serializers.ValidationError('Введите международный номер, например +996…')
        return value
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Укажите имя.')
        return value.strip()

@extend_schema_serializer(component_name='MobileDelivery')
class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['name', 'status', 'channel', 'attempts']

@extend_schema_serializer(component_name='MobileAlert')
class AlertSerializer(serializers.ModelSerializer):
    deliveries = DeliverySerializer(many=True, read_only=True)
    class Meta:
        model = Alert
        fields = ['id', 'request_id', 'created_at', 'reason', 'latitude', 'longitude', 'location_accuracy', 'location_at', 'resolved_at', 'deliveries']

@extend_schema_serializer(component_name='MobileAlertInput')
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

@extend_schema_serializer(component_name='MobileJourney')
class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ['id', 'destination', 'deadline', 'state', 'created_at', 'alert']
        read_only_fields = ['state', 'created_at', 'alert']
