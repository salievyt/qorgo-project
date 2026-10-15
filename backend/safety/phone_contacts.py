"""Exact phone matching; never expose account email or upload an address book."""
import phonenumbers
from django.contrib.auth import get_user_model
from rest_framework import serializers


def normalize_phone(value):
    try:
        phone = phonenumbers.parse(value.strip(), 'KG')
        if not phonenumbers.is_possible_number(phone):
            raise ValueError()
        return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
    except (phonenumbers.NumberParseException, ValueError):
        raise serializers.ValidationError('Укажите корректный номер, например +996700123456.')


def registered_user(phone, owner):
    return get_user_model().objects.filter(
        phone_number=phone, is_active=True, is_deleted=False,
    ).exclude(pk=owner.pk).select_related('privacy_settings').first()


class PhoneLookupInput(serializers.Serializer):
    phone = serializers.CharField(max_length=40)
    def validate_phone(self, value):
        return normalize_phone(value)


class PhoneLookupOutput(serializers.Serializer):
    registered = serializers.BooleanField()
    phone = serializers.CharField()
    name = serializers.CharField(required=False)
    already_added = serializers.BooleanField(required=False)
