from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import EmergencyContact, PrivacySettings, DeviceInfo

User = get_user_model()


class PrivacySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacySettings
        fields = ('show_location', 'location_visibility', 'show_profile', 'share_battery_level', 'share_speed')


class DeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceInfo
        fields = ('platform', 'device_model', 'os_version', 'app_version', 'battery_level', 'is_low_power_mode', 'fcm_token')


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ('id', 'name', 'phone_number', 'relationship', 'priority', 'is_verified', 'created_at')
        read_only_fields = ('id', 'is_verified', 'created_at')

    def validate_priority(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError('Priority must be between 1 and 20.')
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        privacy_settings = PrivacySettings.objects.create()
        user = User.objects.create(
            privacy_settings=privacy_settings,
            **validated_data,
        )
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)


class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(min_length=4, max_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    privacy_settings = PrivacySettingsSerializer(read_only=True)
    devices = DeviceInfoSerializer(many=True, read_only=True)
    display_role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'email', 'first_name', 'last_name',
            'photo', 'date_of_birth', 'gender', 'city', 'blood_type',
            'medical_notes', 'role', 'display_role',
            'is_premium', 'premium_expiry',
            'last_active_at', 'date_joined', 'privacy_settings',
            'devices', 'fcm_tokens',
        )
        read_only_fields = ('id', 'role', 'display_role', 'is_premium', 'premium_expiry', 'last_active_at', 'date_joined', 'fcm_tokens')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'photo', 'date_of_birth',
            'gender', 'city', 'blood_type', 'medical_notes',
        )


class PrivacySettingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacySettings
        fields = ('show_location', 'location_visibility', 'show_profile', 'share_battery_level', 'share_speed')


class UserBasicSerializer(serializers.ModelSerializer):
    """Minimal user info for family/location sharing display."""
    display_role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'photo', 'phone_number', 'is_premium', 'role', 'display_role')


class FCMTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return attrs


# ===== Admin Serializers =====

class UserAdminSerializer(serializers.ModelSerializer):
    """Full user serializer for admin panel."""
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'last_login', 'date_joined', 'last_active_at')


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating user role."""
    role = serializers.ChoiceField(choices=['user', 'admin', 'emergency_operator'])
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)


class UserBlockSerializer(serializers.Serializer):
    """Serializer for blocking/unblocking users."""
    is_active = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)
