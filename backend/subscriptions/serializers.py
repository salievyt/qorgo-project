from rest_framework import serializers
from .models import SubscriptionPlan, Subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            'id', 'plan_type', 'name', 'description',
            'price_usd', 'price_som',
            'max_family_members', 'history_retention_days',
            'ai_safety_analysis', 'video_recording',
            'cloud_backup', 'priority_notifications',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id', 'user', 'plan', 'status', 'started_at',
            'expires_at', 'canceled_at', 'auto_renew',
            'payment_provider',
        )
        read_only_fields = ('id', 'user', 'started_at')


class StartSubscriptionSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=SubscriptionPlan.PlanType.choices)
    payment_provider = serializers.ChoiceField(choices=Subscription.PaymentProvider.choices)
    payment_provider_id = serializers.CharField(required=False, allow_blank=True)
