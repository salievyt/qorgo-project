from common.schema import MessageSerializer
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import inline_serializer, extend_schema

from .models import SafetyTimer
from .serializers import (
    SafetyTimerSerializer, SafetyTimerCreateSerializer,
    ConfirmArrivalSerializer,
)


@extend_schema(summary='Create safety timer', tags=['Safety Timer'])
class CreateSafetyTimerView(APIView):
    @extend_schema(request=SafetyTimerCreateSerializer, responses={201: SafetyTimerSerializer})
    def post(self, request):
        serializer = SafetyTimerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estimated_arrival = timezone.now() + timezone.timedelta(
            minutes=serializer.validated_data['estimated_arrival_minutes']
        )

        timer = SafetyTimer.objects.create(
            user=request.user,
            destination_latitude=serializer.validated_data['destination_latitude'],
            destination_longitude=serializer.validated_data['destination_longitude'],
            destination_address=serializer.validated_data['destination_address'],
            estimated_arrival_at=estimated_arrival,
            auto_trigger_alert=serializer.validated_data.get('auto_trigger_alert', False),
        )

        return Response(
            SafetyTimerSerializer(timer, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(summary='List user safety timers', tags=['Safety Timer'])
class SafetyTimerListView(generics.ListAPIView):
    serializer_class = SafetyTimerSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SafetyTimer.objects.none()
        return SafetyTimer.objects.filter(user=self.request.user)


@extend_schema(summary='Confirm arrival', tags=['Safety Timer'])
class ConfirmArrivalView(APIView):
    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request, timer_id):
        try:
            timer = SafetyTimer.objects.get(id=timer_id, user=request.user)
        except SafetyTimer.DoesNotExist:
            return Response({'error': 'Timer not found.'}, status=status.HTTP_404_NOT_FOUND)

        if timer.status != SafetyTimer.Status.ACTIVE:
            return Response({'error': 'Timer is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        timer.status = SafetyTimer.Status.ARRIVED
        timer.save(update_fields=['status'])

        return Response({'message': 'Arrival confirmed.'})


@extend_schema(summary='Cancel safety timer', tags=['Safety Timer'])
class CancelSafetyTimerView(APIView):
    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request, timer_id):
        try:
            timer = SafetyTimer.objects.get(id=timer_id, user=request.user)
        except SafetyTimer.DoesNotExist:
            return Response({'error': 'Timer not found.'}, status=status.HTTP_404_NOT_FOUND)

        if timer.status != SafetyTimer.Status.ACTIVE:
            return Response({'error': 'Timer is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        timer.status = SafetyTimer.Status.CANCELLED
        timer.save(update_fields=['status'])

        return Response({'message': 'Timer cancelled.'})
