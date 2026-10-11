from common.schema import SuccessSerializer
from django.db import transaction
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import inline_serializer, extend_schema

from .models import LocationUpdate, ActiveLocation
from .serializers import (
    LocationUpdateCreateSerializer, ActiveLocationSerializer,
    LocationHistorySerializer, FamilyLocationSerializer,
)
from families.models import Family, FamilyMembership
from accounts.models import User


@extend_schema(summary='Update user location', tags=['Location'])
class UpdateLocationView(APIView):
    throttle_scope = 'location_update'

    @extend_schema(request=LocationUpdateCreateSerializer, responses=SuccessSerializer)
    def post(self, request):
        serializer = LocationUpdateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Save to history
            LocationUpdate.objects.create(
                user=request.user,
                **serializer.validated_data,
            )

            # Update active location
            ActiveLocation.objects.update_or_create(
                user=request.user,
                defaults={
                    'latitude': serializer.validated_data['latitude'],
                    'longitude': serializer.validated_data['longitude'],
                    'accuracy': serializer.validated_data.get('accuracy', 0),
                    'speed': serializer.validated_data.get('speed', 0),
                    'battery_level': serializer.validated_data.get('battery_level', 100),
                    'is_stale': False,
                },
            )

        # Update user's last active timestamp
        User.objects.filter(id=request.user.id).update(last_active_at=timezone.now())

        return Response({'success': True})


@extend_schema(summary='Get family locations', tags=['Location'])
class FamilyLocationsView(APIView):
    @extend_schema(request=None, responses=FamilyLocationSerializer(many=True))
    def get(self, request, family_id):
        try:
            family = Family.objects.get(id=family_id, members=request.user)
        except Family.DoesNotExist:
            return Response({'error': 'Family not found or not a member.'}, status=status.HTTP_404_NOT_FOUND)

        members = User.objects.filter(families=family).exclude(id=request.user.id)

        locations = []
        for member in members:
            try:
                active_loc = ActiveLocation.objects.get(user=member)
                location = ActiveLocationSerializer(active_loc).data
            except ActiveLocation.DoesNotExist:
                location = None

            locations.append({
                'user': {
                    'id': str(member.id),
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'photo': request.build_absolute_uri(member.photo.url) if member.photo else None,
                    'phone_number': str(member.phone_number),
                },
                'location': location,
            })

        return Response(locations)


@extend_schema(summary='Get location history', tags=['Location'])
class LocationHistoryView(generics.ListAPIView):
    serializer_class = LocationHistorySerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LocationUpdate.objects.none()
        return LocationUpdate.objects.filter(user=self.request.user)[:500]


@extend_schema(summary='Get current user location', tags=['Location'])
class MyLocationView(APIView):
    @extend_schema(request=None, responses={200: {'oneOf': [{'$ref': '#/components/schemas/ActiveLocation'}, {'type': 'object', 'properties': {'location': {'type': 'object', 'nullable': True}}}]}})
    def get(self, request):
        try:
            location = ActiveLocation.objects.get(user=request.user)
            return Response(ActiveLocationSerializer(location).data)
        except ActiveLocation.DoesNotExist:
            return Response({'location': None})
