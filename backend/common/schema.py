"""Response contracts shared by the API documentation."""
from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class LegacyProfileSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_blank=True)


class LegacyProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    phone_number = serializers.CharField(max_length=40, allow_blank=True, required=False)


class CapabilitiesSerializer(serializers.Serializer):
    sms = serializers.BooleanField()
    email = serializers.BooleanField()


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class NotificationInputSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    body = serializers.CharField(required=False)


class PremiumStatusSerializer(serializers.Serializer):
    is_premium = serializers.BooleanField()
    premium_expiry = serializers.DateTimeField(allow_null=True)
