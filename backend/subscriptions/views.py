from common.schema import MessageSerializer, PremiumStatusSerializer
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import inline_serializer, extend_schema

from .models import SubscriptionPlan, Subscription
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer,
    StartSubscriptionSerializer,
)


@extend_schema(summary='List available subscription plans', tags=['Subscriptions'])
class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.filter(is_active=True).order_by('price_usd', 'pk')
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(summary='Get current user subscription', tags=['Subscriptions'])
class MySubscriptionView(APIView):
    @extend_schema(request=None, responses={200: {'oneOf': [{'$ref': '#/components/schemas/Subscription'}, {'type': 'object', 'properties': {'subscription': {'type': 'object', 'nullable': True}}}]}})
    def get(self, request):
        active_sub = Subscription.objects.filter(
            user=request.user,
            status__in=['active', 'trial'],
        ).first()

        if active_sub:
            return Response(SubscriptionSerializer(active_sub).data)
        return Response({'subscription': None})


@extend_schema(summary='Start/upgrade subscription', tags=['Subscriptions'])
class StartSubscriptionView(APIView):
    @extend_schema(request=StartSubscriptionSerializer, responses={201: SubscriptionSerializer})
    def post(self, request):
        serializer = StartSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            plan = SubscriptionPlan.objects.get(
                plan_type=serializer.validated_data['plan_type'],
                is_active=True,
            )
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Invalid plan.'}, status=status.HTTP_400_BAD_REQUEST)

        # Cancel existing active subscriptions
        Subscription.objects.filter(
            user=request.user,
            status__in=['active', 'trial'],
        ).update(status='canceled', canceled_at=timezone.now())

        # Calculate expiry
        is_yearly = 'yearly' in plan.plan_type
        from datetime import timedelta
        expiry = timezone.now() + (timedelta(days=365) if is_yearly else timedelta(days=30))

        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='active',
            expires_at=expiry,
            auto_renew=True,
            payment_provider=serializer.validated_data.get('payment_provider', 'admin'),
            payment_provider_id=serializer.validated_data.get('payment_provider_id', ''),
        )

        # Update user premium status
        request.user.is_premium = True
        request.user.premium_expiry = expiry
        request.user.save(update_fields=['is_premium', 'premium_expiry'])

        # Upgrade family plans
        from families.models import Family
        families = Family.objects.filter(created_by=request.user)
        for family in families:
            family.is_premium = True
            family.max_members = plan.max_family_members
            family.save(update_fields=['is_premium', 'max_members'])

        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(summary='Cancel subscription', tags=['Subscriptions'])
class CancelSubscriptionView(APIView):
    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request):
        active_sub = Subscription.objects.filter(
            user=request.user,
            status='active',
        ).first()

        if not active_sub:
            return Response({'error': 'No active subscription.'}, status=status.HTTP_400_BAD_REQUEST)

        active_sub.status = 'canceled'
        active_sub.canceled_at = timezone.now()
        active_sub.auto_renew = False
        active_sub.save(update_fields=['status', 'canceled_at', 'auto_renew'])

        request.user.is_premium = False
        request.user.save(update_fields=['is_premium'])

        return Response({'message': 'Subscription canceled.'})


@extend_schema(summary='Check premium status', tags=['Subscriptions'])
class PremiumStatusView(APIView):
    @extend_schema(request=None, responses=PremiumStatusSerializer)
    def get(self, request):
        return Response({
            'is_premium': request.user.is_premium,
            'premium_expiry': request.user.premium_expiry,
        })
