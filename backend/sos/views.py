from django.utils import timezone
from django.shortcuts import get_object_or_404
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
    """Unified queue for current and legacy mobile SOS requests."""
    permission_classes = [permissions.IsAuthenticated, IsEmergencyOperator]
    serializer_class = OperatorIncidentSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Alert.objects.none()
        return Alert.objects.select_related('user', 'assigned_operator').filter(
            status=Alert.Status.ACTIVE,
        ).order_by('assigned_at', '-started_at')

    def list(self, request, *args, **kwargs):
        from safety.models import Alert as MobileAlert
        current = list(OperatorIncidentSerializer(self.get_queryset(), many=True).data)
        mobile_alerts = MobileAlert.objects.select_related('owner', 'assigned_operator').filter(
            resolved_at__isnull=True,
        ).order_by('assigned_at', '-created_at')
        current.extend(self.serialize_mobile_alert(alert) for alert in mobile_alerts)
        current.sort(key=lambda row: row.get('started_at') or '', reverse=True)
        current.sort(key=lambda row: bool(row.get('assigned_operator')))
        return Response({'results': current})

    @staticmethod
    def serialize_mobile_alert(alert):
        return {
            'id': f'mvp-{alert.pk}',
            'status': 'active',
            'trigger_method': alert.reason,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'address': '',
            'battery_level': 0,
            'started_at': alert.created_at.isoformat(),
            'resolved_at': alert.resolved_at,
            'assigned_operator': str(alert.assigned_operator_id) if alert.assigned_operator_id else None,
            'assigned_operator_name': (
                alert.assigned_operator.get_full_name().strip()
                or alert.assigned_operator.phone_number
                or 'Оператор QORGO'
            ) if alert.assigned_operator_id else '',
            'assigned_at': alert.assigned_at.isoformat() if alert.assigned_at else None,
            'operator_note': alert.operator_note,
            'user': {
                'id': str(alert.owner_id),
                'first_name': alert.owner.first_name,
                'last_name': alert.owner.last_name,
                'phone_number': str(alert.owner.phone_number or ''),
            },
        }


@extend_schema(tags=['QORGO Agent'])
class OperatorIncidentDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsEmergencyOperator]
    serializer_class = OperatorIncidentSerializer
    queryset = Alert.objects.select_related('user', 'assigned_operator')

    def retrieve(self, request, *args, **kwargs):
        alert_id = self.kwargs['pk']
        if alert_id.startswith('mvp-') and alert_id[4:].isdigit():
            from safety.models import Alert as MobileAlert
            alert = get_object_or_404(MobileAlert.objects.select_related('owner', 'assigned_operator'), pk=int(alert_id[4:]))
            return Response(OperatorIncidentListView.serialize_mobile_alert(alert))
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=['QORGO Agent'])
class OperatorTakeIncidentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsEmergencyOperator]

    @extend_schema(request=None, responses=OperatorIncidentSerializer)
    def post(self, request, alert_id):
        if alert_id.startswith('mvp-') and alert_id[4:].isdigit():
            from safety.models import Alert as MobileAlert
            with transaction.atomic():
                alert = MobileAlert.objects.select_for_update().select_related('owner', 'assigned_operator').filter(
                    id=int(alert_id[4:]), resolved_at__isnull=True,
                ).first()
                if not alert:
                    return Response({'detail': 'Активный инцидент не найден.'}, status=status.HTTP_404_NOT_FOUND)
                if alert.assigned_operator_id and alert.assigned_operator_id != request.user.id:
                    return Response({'detail': 'Инцидент уже принят другим оператором.'}, status=status.HTTP_409_CONFLICT)
                if not alert.assigned_operator_id:
                    alert.assigned_operator = request.user
                    alert.assigned_at = timezone.now()
                    alert.save(update_fields=['assigned_operator', 'assigned_at'])
            return Response(OperatorIncidentListView.serialize_mobile_alert(alert))
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
        if alert_id.startswith('mvp-') and alert_id[4:].isdigit():
            from safety.models import Alert as MobileAlert
            with transaction.atomic():
                alert = MobileAlert.objects.select_for_update().select_related('owner', 'assigned_operator').filter(
                    id=int(alert_id[4:]), resolved_at__isnull=True,
                ).first()
                if not alert:
                    return Response({'detail': 'Активный инцидент не найден.'}, status=status.HTTP_404_NOT_FOUND)
                if alert.assigned_operator_id != request.user.id:
                    return Response({'detail': 'Сначала примите инцидент в работу.'}, status=status.HTTP_403_FORBIDDEN)
                alert.operator_note = data.validated_data.get('note', alert.operator_note)
                alert.resolved_at = timezone.now()
                alert.save(update_fields=['operator_note', 'resolved_at'])
            return Response(OperatorIncidentListView.serialize_mobile_alert(alert))
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
