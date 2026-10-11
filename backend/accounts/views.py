from common.schema import MessageSerializer, PhoneSerializer
from rest_framework import serializers
import random
from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import inline_serializer, extend_schema, OpenApiParameter

from .serializers import (
    UserLoginSerializer, UserRegistrationSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    PrivacySettingsSerializer, PrivacySettingsUpdateSerializer,
    EmergencyContactSerializer, UserBasicSerializer,
    FCMTokenSerializer, ChangePasswordSerializer, OTPSerializer,
    UserAdminSerializer, UserRoleUpdateSerializer, UserBlockSerializer,
)
from .models import EmergencyContact, PrivacySettings, DeviceInfo
from common.permissions import IsAdmin, IsSuperAdmin

User = get_user_model()


# ===== Registration & Auth =====

@extend_schema(
    summary='Register a new user',
    tags=['Authentication'],
)
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={201: inline_serializer('JWTRegistrationResponse', fields={'user': UserProfileSerializer(), 'access': serializers.CharField(), 'refresh': serializers.CharField()})})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Request OTP for phone verification',
    tags=['Authentication'],
)
class RequestOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=PhoneSerializer, responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}, 'otp': {'type': 'string'}, 'debug': {'type': 'boolean'}}}})
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate 6-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Store OTP in cache for 5 minutes
        cache.set(f'otp_{phone_number}', otp, timeout=300)
        
        # TODO: Integrate with SMS provider to send the OTP
        # For now, log it (for development)
        print(f'[OTP] {phone_number}: {otp}')
        
        # In development, return the OTP
        from django.conf import settings
        if settings.DEBUG:
            return Response({'message': 'OTP sent', 'otp': otp, 'debug': True})
        
        return Response({'message': 'OTP sent successfully'})


@extend_schema(
    summary='Verify OTP and login',
    tags=['Authentication'],
)
class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=OTPSerializer, responses=inline_serializer('OTPLoginResponse', fields={'user': UserProfileSerializer(), 'access': serializers.CharField(), 'refresh': serializers.CharField(), 'is_new': serializers.BooleanField()}))
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        cached_otp = cache.get(f'otp_{phone_number}')
        if not cached_otp or cached_otp != otp_code:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP
        cache.delete(f'otp_{phone_number}')

        # Find or create user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'email': f'{phone_number.replace("+", "")}@qorgo.app',
                'first_name': 'User',
                'last_name': phone_number[-4:],
                'privacy_settings': PrivacySettings.objects.create(),
            }
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'is_new': created,
        })


@extend_schema(
    summary='Login with phone and password',
    tags=['Authentication'],
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=UserLoginSerializer, responses=inline_serializer('JWTLoginResponse', fields={'user': UserProfileSerializer(), 'access': serializers.CharField(), 'refresh': serializers.CharField()}))
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone_number or not password:
            return Response({'error': 'Phone number and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=phone_number, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


# ===== Profile =====

@extend_schema(
    summary='Get current user profile',
    tags=['Profile'],
)
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


@extend_schema(
    summary='Update current user profile',
    tags=['Profile'],
)
class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save()
        # Refresh user data cache
        return serializer


@extend_schema(
    summary='Update privacy settings',
    tags=['Profile'],
)
class PrivacySettingsUpdateView(generics.UpdateAPIView):
    serializer_class = PrivacySettingsUpdateSerializer

    def get_object(self):
        user = self.request.user
        if not hasattr(user, 'privacy_settings') or user.privacy_settings is None:
            user.privacy_settings = PrivacySettings.objects.create()
            user.save()
        return user.privacy_settings


@extend_schema(
    summary='Change password',
    tags=['Profile'],
)
class ChangePasswordView(APIView):
    @extend_schema(request=ChangePasswordSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully.'})


@extend_schema(
    summary='Update FCM token for push notifications',
    tags=['Profile'],
)
class UpdateFCMTokenView(APIView):
    @extend_schema(request=FCMTokenSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        token = serializer.validated_data['token']

        if token not in user.fcm_tokens:
            user.fcm_tokens.append(token)
            user.save(update_fields=['fcm_tokens'])

        return Response({'message': 'FCM token updated.'})


@extend_schema(
    summary='Remove FCM token',
    tags=['Profile'],
)
class RemoveFCMTokenView(APIView):
    @extend_schema(request=FCMTokenSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        token = serializer.validated_data['token']

        if token in user.fcm_tokens:
            user.fcm_tokens.remove(token)
            user.save(update_fields=['fcm_tokens'])

        return Response({'message': 'FCM token removed.'})


# ===== Emergency Contacts =====

@extend_schema(
    summary='List emergency contacts',
    tags=['Emergency Contacts'],
)
class EmergencyContactListView(generics.ListCreateAPIView):
    serializer_class = EmergencyContactSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return EmergencyContact.objects.none()
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    summary='Get, update, or delete an emergency contact',
    tags=['Emergency Contacts'],
)
class EmergencyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmergencyContactSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return EmergencyContact.objects.none()
        return EmergencyContact.objects.filter(user=self.request.user)


# ===== Users search (for family invites) =====

@extend_schema(
    summary='Search users by phone number',
    tags=['Users'],
)
class UserSearchView(generics.ListAPIView):
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        query = self.request.query_params.get('q', '')
        if not query:
            return User.objects.none()
        return User.objects.filter(
            phone_number__icontains=query,
            is_deleted=False,
        ).exclude(id=self.request.user.id)[:20]


# ===== Admin: User Management =====

@extend_schema(summary='Admin: List all users', tags=['Admin'])
class AdminUserListView(generics.ListAPIView):
    """List all users (admin only)."""
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    ordering_fields = ('date_joined', 'last_active_at', 'role')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        qs = User.objects.filter(is_deleted=False)
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        
        # Filter by premium status
        premium = self.request.query_params.get('premium')
        if premium == 'true':
            qs = qs.filter(is_premium=True)
        elif premium == 'false':
            qs = qs.filter(is_premium=False)
            
        return qs.order_by('-date_joined')


@extend_schema(summary='Admin: Get user details', tags=['Admin'])
class AdminUserDetailView(generics.RetrieveAPIView):
    """Get any user's full details."""
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


@extend_schema(summary='Admin: Update user role', tags=['Admin'])
class AdminUpdateRoleView(APIView):
    """Update a user's role (admin only)."""
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    @extend_schema(request=UserRoleUpdateSerializer, responses=UserAdminSerializer)
    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_role = serializer.validated_data['role']
        target_user.role = new_role
        
        if 'is_staff' in serializer.validated_data:
            target_user.is_staff = serializer.validated_data['is_staff']
        if 'is_superuser' in serializer.validated_data:
            target_user.is_superuser = serializer.validated_data['is_superuser']
        
        # Auto-set is_staff for admin roles
        if new_role == 'admin':
            target_user.is_staff = True
        elif new_role == 'user':
            target_user.is_staff = False
            target_user.is_superuser = False
            
        target_user.save(update_fields=['role', 'is_staff', 'is_superuser'])
        
        return Response(UserAdminSerializer(target_user).data)


@extend_schema(summary='Admin: Block/unblock user', tags=['Admin'])
class AdminBlockUserView(APIView):
    """Block or unblock a user account."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    @extend_schema(request=UserBlockSerializer, responses=MessageSerializer)
    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Super admins cannot be blocked by regular admins
        if target_user.is_superuser and not request.user.is_superuser:
            return Response({'error': 'Cannot block a super admin.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserBlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user.is_active = serializer.validated_data['is_active']
        target_user.save(update_fields=['is_active'])

        action = 'blocked' if not target_user.is_active else 'unblocked'
        return Response({'message': f'User {action} successfully.'})


@extend_schema(summary='Admin: List SOS alerts', tags=['Admin'])
class AdminSOSListView(generics.ListAPIView):
    """View all SOS alerts (admin only)."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    ordering_fields = ('-started_at',)

    def get_queryset(self):
        from sos.models import Alert
        qs = Alert.objects.all()
        
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
            
        return qs.order_by('-started_at')

    def get_serializer_class(self):
        from sos.serializers import AlertSerializer
        return AlertSerializer


@extend_schema(summary='Admin: Dashboard stats', tags=['Admin'])
class AdminDashboardView(APIView):
    """Get system-wide statistics for admin panel."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    @extend_schema(request=None, responses={200: {'type': 'object', 'additionalProperties': True}})
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        from sos.models import Alert
        from families.models import Family
        today = timezone.now()
        last_30d = today - timedelta(days=30)

        return Response({
            'total_users': User.objects.filter(is_deleted=False).count(),
            'users_by_role': {
                'user': User.objects.filter(role='user', is_deleted=False).count(),
                'admin': User.objects.filter(role='admin', is_deleted=False).count(),
                'emergency_operator': User.objects.filter(role='emergency_operator', is_deleted=False).count(),
            },
            'new_users_30d': User.objects.filter(date_joined__gte=last_30d).count(),
            'active_users_30d': User.objects.filter(last_active_at__gte=last_30d, is_deleted=False).count(),
            'premium_users': User.objects.filter(is_premium=True, is_deleted=False).count(),
            'total_alerts': Alert.objects.count(),
            'active_alerts': Alert.objects.filter(status='active').count(),
            'alerts_30d': Alert.objects.filter(started_at__gte=last_30d).count(),
            'total_families': Family.objects.count(),
            'blocked_users': User.objects.filter(is_active=False, is_deleted=False).count(),
        })
