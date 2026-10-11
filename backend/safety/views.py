from drf_spectacular.utils import extend_schema
from common.schema import TokenSerializer, LegacyProfileSerializer, LegacyProfileUpdateSerializer, CapabilitiesSerializer
from datetime import timedelta
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from accounts.models import PrivacySettings
from .models import Contact, Alert, Journey
from .serializers import ContactSerializer, AlertSerializer, AlertInputSerializer, JourneySerializer
from .services import create_alert, finish_journey, process_deadlines

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
        field = serializers.CharField(max_length=100, allow_blank=False)
        request.user.first_name = field.run_validation(request.data.get('name', ''))
        request.user.save(update_fields=['first_name'])
    return Response({'name': request.user.first_name, 'email': request.user.email})

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
        return Contact.objects.filter(owner=self.request.user).order_by('id')
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
        alert.deliveries.filter(status__in=['pending', 'unconfigured']).update(status='cancelled')
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
