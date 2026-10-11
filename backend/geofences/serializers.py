from rest_framework import serializers
from .models import Geofence, GeofenceEvent


class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class GeofenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        exclude = ('user', 'family_notification_list')
        read_only_fields = ('id', 'created_at', 'updated_at')


class GeofenceEventSerializer(serializers.ModelSerializer):
    geofence_name = serializers.CharField(source='geofence.name', read_only=True)

    class Meta:
        model = GeofenceEvent
        fields = ('id', 'geofence', 'geofence_name', 'event_type', 'latitude', 'longitude', 'timestamp')
