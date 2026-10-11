from rest_framework import serializers
from .models import LocationUpdate, ActiveLocation
from accounts.serializers import UserBasicSerializer


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationUpdate
        fields = (
            'latitude', 'longitude', 'accuracy', 'altitude',
            'speed', 'heading', 'battery_level', 'is_background',
        )


class LocationUpdateCreateSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    accuracy = serializers.FloatField(default=0)
    altitude = serializers.FloatField(required=False, allow_null=True)
    speed = serializers.FloatField(default=0)
    heading = serializers.FloatField(default=0)
    battery_level = serializers.FloatField(default=100)
    is_background = serializers.BooleanField(default=False)


class ActiveLocationSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = ActiveLocation
        fields = ('user', 'latitude', 'longitude', 'accuracy', 'speed', 'battery_level', 'is_stale', 'last_updated')


class LocationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationUpdate
        fields = ('latitude', 'longitude', 'speed', 'battery_level', 'is_background', 'timestamp')


class FamilyLocationSerializer(serializers.Serializer):
    """Serializer for family location view with user info."""
    user = UserBasicSerializer()
    location = ActiveLocationSerializer(allow_null=True)
