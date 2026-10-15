from django.utils import timezone
from django.db import transaction
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import inline_serializer, extend_schema

from .models import Alert, EvidenceRecording
from .serializers import (
    AlertSerializer, AlertListSerializer, CreateAlertSerializer,
    ResolveAlertSerializer, EvidenceSerializer, OperatorIncidentSerializer,
    OperatorIncidentUpdateSerializer,
)
from common.services import generate_map_link
from families.models import FamilyMembership
from notifications.services import send_sos_alert_to_contacts, notify_family_members
from common.permissions import IsEmergencyOperator


@extend_schema(summary='Create SOS alert', tags=['SOS'])
class CreateAlertView(APIView):
    throttle_scope = 'sos'

    @extend_schema(request=CreateAlertSerializer, responses={201: AlertSerializer})
    def post(self, request):
        serializer = CreateAlertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Create alert
            alert = Alert.objects.create(
                user=request.user,
                status=Alert.Status.ACTIVE,
                trigger_method=serializer.validated_data['trigger_method'],
                latitude=serializer.validated_data['latitude'],
                longitude=serializer.validated_data['longitude'],
                address=serializer.validated_data.get('address', ''),
                map_link=generate_map_link(
                    serializer.validated_data['latitude'],
                    serializer.validated_data['longitude'],
                ),
                battery_level=serializer.validated_data.get('battery_level', 0),
            )

            # Get emergency contacts
            contacts = request.user.emergency_contact_relations.all()

            # Send notifications
            notified = send_sos_alert_to_contacts(
                alert, request.user, contacts,
            )

            # Notify families
            families = request.user.families.all()
            for family in families:
                notify_family_members(
                    family, request.user,
                    '🚨 SOS Alert!',
                    f'{request.user.first_name} {request.user.last_name} has activated SOS!',
                    {'type': 'sos_alert', 'alert_id': str(alert.id)},
                )

            # Update alert
            alert.notified_contacts = notified
            alert.family_notified = families.exists()
            alert.save(update_fields=['notified_contacts', 'family_notified'])

        return Response(
            AlertSerializer(alert, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(summary='List user alerts', tags=['SOS'])
class AlertListView(generics.ListAPIView):
    serializer_class = AlertListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Alert.objects.none()
        return Alert.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # If detail requested, user full serializer
        if self.request.query_params.get('detail'):
            self.serializer_class = AlertSerializer
        return context


@extend_schema(summary='Get alert details', tags=['SOS'])
class AlertDetailView(generics.RetrieveAPIView):
    serializer_class = AlertSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Alert.objects.none()
        return Alert.objects.filter(user=self.request.user)


@extend_schema(summary='Resolve SOS alert', tags=['SOS'])
class ResolveAlertView(APIView):
    @extend_schema(request=ResolveAlertSerializer, responses=AlertSerializer)
    def post(self, request, alert_id):
        try:
            alert = Alert.objects.get(id=alert_id, user=request.user)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found.'}, status=status.HTTP_404_NOT_FOUND)

        if alert.status != Alert.Status.ACTIVE:
            return Response({'error': 'Alert is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResolveAlertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        alert.status = serializer.validated_data['status']
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save(update_fields=['status', 'resolved_at', 'resolved_by'])

        return Response(AlertSerializer(alert, context={'request': request}).data)


@extend_schema(summary='Upload evidence for alert', tags=['SOS'])
class UploadEvidenceView(generics.CreateAPIView):
    serializer_class = EvidenceSerializer

    def perform_create(self, serializer):
        alert_id = self.kwargs.get('alert_id')
        alert = Alert.objects.get(id=alert_id, user=self.request.user)
        serializer.save(alert=alert, user=self.request.user)


@extend_schema(summary='List evidence for alert', tags=['SOS'])
class AlertEvidenceListView(generics.ListAPIView):
    serializer_class = EvidenceSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return EvidenceRecording.objects.none()
        return EvidenceRecording.objects.filter(
            alert_id=self.kwargs['alert_id'],
            alert__user=self.request.user,
        )


@extend_schema(tags=['QORGO Agent'])
class OperatorIncidentListView(generics.ListAPIView):
    """Queue for responders. Operators only receive active incidents and their own history."""
    permission_classes = [permissions.IsAuthenticated, IsEmergencyOperator]
    serializer_class = OperatorIncidentSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Alert.objects.none()
        return Alert.objects.select_related('user', 'assigned_operator').filter(
            status=Alert.Status.ACTIVE,
        ).order_by('assigned_at', '-started_at')


@extend_schema(tags=['QORGO Agent'])
class OperatorIncidentDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsEmergencyOperator]
    serializer_class = OperatorIncidentSerializer
    queryset = Alert.objects.select_related('user', 'assigned_operator')


@extend_schema(tags=['QORGO Agent'])
class OperatorTakeIncidentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsEmergencyOperator]

    @extend_schema(request=None, responses=OperatorIncidentSerializer)
    def post(self, request, alert_id):
        with transaction.atomic():
            alert = Alert.objects.select_for_update().select_related('assigned_operator').filter(
                id=alert_id, status=Alert.Status.ACTIVE).first()
            if not alert:
                return Response({'detail': 'Активный инцидент не найден.'}, status=status.HTTP_404_NOT_FOUND)
            if alert.assigned_operator_id and alert.assigned_operator_id != request.user.id:
                return Response({'detail': 'Инцидент уже принят другим оператором.'}, status=status.HTTP_409_CONFLICT)
            if not alert.assigned_operator_id:
                alert.assigned_operator = request.user
                alert.assigned_at = timezone.now()
                alert.save(update_fields=['assigned_operator', 'assigned_at'])
        return Response(OperatorIncidentSerializer(alert).data)


@extend_schema(tags=['QORGO Agent'])
class OperatorCloseIncidentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsEmergencyOperator]

    @extend_schema(request=OperatorIncidentUpdateSerializer, responses=OperatorIncidentSerializer)
    def post(self, request, alert_id):
        data = OperatorIncidentUpdateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        with transaction.atomic():
            alert = Alert.objects.select_for_update().select_related('assigned_operator').filter(
                id=alert_id, status=Alert.Status.ACTIVE).first()
            if not alert:
                return Response({'detail': 'Активный инцидент не найден.'}, status=status.HTTP_404_NOT_FOUND)
            if alert.assigned_operator_id != request.user.id:
                return Response({'detail': 'Сначала примите инцидент в работу.'}, status=status.HTTP_403_FORBIDDEN)
            alert.status = data.validated_data.get('status', Alert.Status.RESOLVED)
            alert.operator_note = data.validated_data.get('note', alert.operator_note)
            alert.resolved_at = timezone.now()
            alert.resolved_by = request.user
            alert.save(update_fields=['status', 'operator_note', 'resolved_at', 'resolved_by'])
        return Response(OperatorIncidentSerializer(alert).data)
