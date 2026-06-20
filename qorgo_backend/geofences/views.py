from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Geofence, GeofenceEvent
from .serializers import GeofenceSerializer, GeofenceCreateSerializer, GeofenceEventSerializer


@extend_schema(summary='List user geofences', tags=['Geofences'])
class GeofenceListView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GeofenceCreateSerializer
        return GeofenceSerializer

    def get_queryset(self):
        return Geofence.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(summary='Get, update, delete a geofence', tags=['Geofences'])
class GeofenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GeofenceSerializer

    def get_queryset(self):
        return Geofence.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


@extend_schema(summary='List geofence events (entry/exit history)', tags=['Geofences'])
class GeofenceEventListView(generics.ListAPIView):
    serializer_class = GeofenceEventSerializer

    def get_queryset(self):
        return GeofenceEvent.objects.filter(user=self.request.user)
