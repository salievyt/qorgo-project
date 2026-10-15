from drf_spectacular.utils import extend_schema
from common.schema import TokenSerializer, LegacyProfileSerializer, LegacyProfileUpdateSerializer, CapabilitiesSerializer
from datetime import timedelta
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from accounts.models import PrivacySettings
from .models import Contact, Alert, Journey
from .serializers import ContactSerializer, AlertSerializer, AlertInputSerializer, JourneySerializer
from .services import create_alert, finish_journey, process_deadlines
from .phone_contacts import normalize_phone, registered_user, PhoneLookupInput, PhoneLookupOutput
from rest_framework.throttling import UserRateThrottle
from location.models import LocationUpdate, ActiveLocation

class Credentials(serializers.Serializer):
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(max_length=128, trim_whitespace=False)
    name = serializers.CharField(max_length=100, required=False, default='')

@extend_schema(tags=['Mobile MVP'], request=Credentials, responses={201: TokenSerializer})
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def register(request):
    data = Credentials(data=request.data)
    data.is_valid(raise_exception=True)
    values = data.validated_data
    email = values['email'].lower()
    User = get_user_model()
    candidate = User(email=email, first_name=values['name'])
    try:
        validate_password(values['password'], candidate)
    except ValidationError as exc:
        return Response({'detail': ' '.join(exc.messages)}, status=400)
    try:
        with transaction.atomic():
            candidate.set_password(values['password'])
            candidate.privacy_settings = PrivacySettings.objects.create()
            candidate.save()
            token = Token.objects.create(user=candidate)
    except IntegrityError:
        return Response({'detail': 'Этот email уже зарегистрирован.'}, status=400)
    return Response({'token': token.key}, status=201)

@extend_schema(tags=['Mobile MVP'], request=Credentials, responses=TokenSerializer)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def login(request):
    data = Credentials(data=request.data)
    data.is_valid(raise_exception=True)
    user = authenticate(email=data.validated_data['email'].lower(), password=data.validated_data['password'])
    if user is None:
        return Response({'detail': 'Неверный email или пароль.'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})

@extend_schema(tags=['Mobile MVP'], request=None, responses={204: None})
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def logout(request):
    request.auth.delete()
    return Response(status=204)

@extend_schema(methods=['GET'], responses=LegacyProfileSerializer, tags=['Mobile MVP'])
@extend_schema(methods=['PATCH'], request=LegacyProfileUpdateSerializer, responses=LegacyProfileSerializer, tags=['Mobile MVP'])
@api_view(['GET', 'PATCH'])
@authentication_classes([TokenAuthentication])
def profile(request):
    if request.method == 'PATCH':
        updates = []
        if 'name' in request.data:
            request.user.first_name = serializers.CharField(max_length=100, allow_blank=False).run_validation(request.data['name'])
            updates.append('first_name')
        if 'phone_number' in request.data:
            raw = serializers.CharField(max_length=40, allow_blank=True).run_validation(request.data['phone_number'])
            phone = normalize_phone(raw) if raw else None
            request.user.phone_number = phone
            updates.append('phone_number')
        if not updates:
            return Response({'detail': 'Укажите имя или номер телефона.'}, status=400)
        try:
            with transaction.atomic():
                request.user.save(update_fields=updates)
        except IntegrityError:
            return Response({'detail': 'Этот номер уже используется другим аккаунтом.'}, status=400)
    return Response({'name': request.user.first_name, 'email': request.user.email,
                     'phone_number': str(request.user.phone_number) if request.user.phone_number else ''})

@extend_schema(tags=['Mobile MVP'], responses=CapabilitiesSerializer)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def capabilities(request):
    from django.conf import settings
    return Response({
        'sms': bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM),
        'email': bool(settings.EMAIL_HOST and settings.DEFAULT_FROM_EMAIL),
    })

class ContactViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    pagination_class = None
    serializer_class = ContactSerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Contact.objects.none()
        return Contact.objects.filter(owner=self.request.user).select_related('recipient').order_by('id')
    def perform_destroy(self, instance):
        if Contact.objects.filter(owner=self.request.user).count() <= 1 and Journey.objects.filter(owner=self.request.user, state='active').exists():
            raise serializers.ValidationError({'detail': 'Сначала завершите активное сопровождение.'})
        instance.delete()
    def perform_create(self, serializer):
        if self.get_queryset().count() >= 20:
            raise serializers.ValidationError({'detail': 'Можно добавить до 20 контактов.'})
        try:
            with transaction.atomic():
                serializer.save(owner=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'Этот номер уже добавлен.'})
    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'Этот номер уже добавлен.'})

class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    pagination_class = None
    serializer_class = AlertSerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Alert.objects.none()
        return Alert.objects.filter(owner=self.request.user).prefetch_related('deliveries').order_by('-created_at')[:100] if self.action == 'list' else Alert.objects.filter(owner=self.request.user)
    @extend_schema(request=AlertInputSerializer, responses={201: AlertSerializer, 200: AlertSerializer})
    def create(self, request):
        data = AlertInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        existing = Alert.objects.filter(owner=request.user, request_id=data.validated_data['request_id']).first()
        if existing:
            return Response(AlertSerializer(existing).data)
        if not Contact.objects.filter(owner=request.user).exists():
            return Response({'detail': 'Добавьте хотя бы один доверенный контакт.'}, status=400)
        alert, created = create_alert(request.user, **data.validated_data)
        return Response(AlertSerializer(alert).data, status=201 if created else 200)
    @extend_schema(request=None)
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['resolved_at'])
        alert.deliveries.filter(status__in=['pending', 'unconfigured', 'available']).update(status='cancelled')
        return Response(AlertSerializer(alert).data)
    @extend_schema(request=None)
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        alert = self.get_object()
        if alert.resolved_at:
            return Response({'detail': 'Тревога завершена.'}, status=400)
        alert.deliveries.filter(status='unknown').update(status='pending')
        return Response(AlertSerializer(alert).data)

class JourneyViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    pagination_class = None
    serializer_class = JourneySerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Journey.objects.none()
        process_deadlines()
        return Journey.objects.filter(owner=self.request.user).order_by('-created_at')
    def create(self, request):
        data = JourneySerializer(data=request.data)
        data.is_valid(raise_exception=True)
        deadline = data.validated_data['deadline']
        if not timezone.now() < deadline <= timezone.now()+timedelta(hours=24):
            return Response({'detail': 'Время прибытия должно быть в пределах 24 часов.'}, status=400)
        if not Contact.objects.filter(owner=request.user).exists():
            return Response({'detail': 'Сначала добавьте доверенный контакт.'}, status=400)
        try:
            with transaction.atomic():
                journey = data.save(owner=request.user)
        except IntegrityError:
            return Response({'detail': 'Уже есть активный таймер.'}, status=400)
        return Response(JourneySerializer(journey).data, status=201)
    @extend_schema(request=None)
    @action(detail=True, methods=['post'])
    def arrive(self, request, pk=None):
        get_object_or_404(Journey, id=pk, owner=request.user)
        journey = finish_journey(request.user, pk, 'arrived')
        return Response(JourneySerializer(journey).data)
    @extend_schema(request=None)
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        get_object_or_404(Journey, id=pk, owner=request.user)
        journey = finish_journey(request.user, pk, 'cancelled')
        return Response(JourneySerializer(journey).data)

# New in-app deliveries use an account ID; email remains for legacy deliveries. Sender-owned alert
# endpoints remain separate so recipients cannot cancel another person's SOS.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def inbox(request):
    from .models import Delivery
    recipients = Q(recipient=request.user)
    if request.user.email:
        recipients |= Q(recipient__isnull=True, email__iexact=request.user.email)
    deliveries = Delivery.objects.filter(recipients).exclude(alert__owner=request.user).select_related('alert__owner').order_by('-alert__created_at')[:100]
    return Response([{
        'delivery_id': d.id,
        'sender_name': d.alert.owner.first_name or d.alert.owner.email,
        'acknowledged': d.channel == 'app' and d.status == 'received',
        'alert': AlertSerializer(d.alert).data,
    } for d in deliveries])

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def acknowledge(request, delivery_id):
    from .models import Delivery
    with transaction.atomic():
        delivery = get_object_or_404(
            Delivery.objects.select_for_update(),
            (Q(recipient=request.user) | Q(recipient__isnull=True, email__iexact=request.user.email)) if request.user.email else Q(recipient=request.user),
            id=delivery_id,
        )
        if delivery.alert.owner_id == request.user.id:
            return Response({'detail': 'Нельзя подтвердить собственный SOS.'}, status=400)
        delivery.channel = 'app'
        delivery.status = 'received'
        delivery.save(update_fields=['channel', 'status', 'updated_at'])
    return Response({'acknowledged': True})


class ContactLookupThrottle(UserRateThrottle):
    scope = 'contact_lookup'
    rate = '30/min'


class LocationInput(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    accuracy = serializers.FloatField(min_value=0, default=0)
    speed = serializers.FloatField(min_value=0, default=0)
    is_background = serializers.BooleanField(default=False)


@extend_schema(tags=['Mobile MVP'], request=LocationInput)
@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
def continuous_location(request):
    """Token-authenticated tracking endpoint used by the Flutter MVP.

    Records are retained for 30 days; the latest point is shown in Django admin.
    """
    if request.method == 'GET':
        points = LocationUpdate.objects.filter(user=request.user).order_by('-timestamp')[:100]
        return Response([{'latitude': p.latitude, 'longitude': p.longitude,
                          'accuracy': p.accuracy, 'speed': p.speed,
                          'is_background': p.is_background,
                          'timestamp': p.timestamp} for p in points])
    data = LocationInput(data=request.data)
    data.is_valid(raise_exception=True)
    values = data.validated_data
    with transaction.atomic():
        point = LocationUpdate.objects.create(user=request.user, **values)
        ActiveLocation.objects.update_or_create(user=request.user, defaults={
            'latitude': point.latitude, 'longitude': point.longitude,
            'accuracy': point.accuracy, 'speed': point.speed,
            'is_stale': False,
        })
        LocationUpdate.objects.filter(
            user=request.user, timestamp__lt=timezone.now() - timedelta(days=30)
        ).delete()
    return Response({'recorded_at': point.timestamp}, status=201)


@extend_schema(tags=['Mobile MVP'], request=PhoneLookupInput, responses=PhoneLookupOutput)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@throttle_classes([ContactLookupThrottle])
def lookup_contact(request):
    data = PhoneLookupInput(data=request.data)
    data.is_valid(raise_exception=True)
    phone = data.validated_data['phone']
    if request.user.phone_number and str(request.user.phone_number) == phone:
        return Response({'detail': 'Это ваш номер. Выберите номер близкого.'}, status=400)
    user = registered_user(phone, request.user)
    if user is None:
        return Response({'registered': False, 'phone': phone})
    visible = not user.privacy_settings or user.privacy_settings.show_profile
    return Response({'registered': True, 'phone': phone,
                     'name': user.get_full_name().strip() if visible and user.get_full_name().strip() else 'Пользователь QORGO',
                     'already_added': Contact.objects.filter(Q(phone=phone) | Q(recipient=user), owner=request.user).exists()})
