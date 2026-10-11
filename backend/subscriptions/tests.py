"""
Tests for subscriptions app — Subscription plans, user subscriptions, premium features.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from subscriptions.models import SubscriptionPlan, Subscription


@pytest.mark.django_db
class TestSubscriptionPlanModel:
    """Test SubscriptionPlan model."""

    def test_free_plan(self, free_plan):
        assert free_plan.plan_type == 'free'
        assert free_plan.price_usd == 0
        assert free_plan.max_family_members == 5
        assert free_plan.history_retention_days == 7
        assert free_plan.ai_safety_analysis is False
        assert free_plan.video_recording is False

    def test_premium_plan(self, subscription_plan):
        assert subscription_plan.price_usd == 4.99
        assert subscription_plan.max_family_members == 10
        assert subscription_plan.ai_safety_analysis is True
        assert subscription_plan.video_recording is True
        assert str(subscription_plan) == 'Premium Monthly — $4.99/mo'

    def test_plan_types(self):
        assert SubscriptionPlan.PlanType.FREE == 'free'
        assert SubscriptionPlan.PlanType.PREMIUM_MONTHLY == 'premium_monthly'
        assert SubscriptionPlan.PlanType.FAMILY_YEARLY == 'family_yearly'
        assert SubscriptionPlan.PlanType.CORPORATE == 'corporate'

    def test_unique_plan_type(self):
        SubscriptionPlan.objects.create(
            plan_type='test_plan', name='Test',
            price_usd=0, price_som=0,
        )
        with pytest.raises(Exception):
            SubscriptionPlan.objects.create(
                plan_type='test_plan', name='Test Duplicate',
                price_usd=0, price_som=0,
            )


class TestSubscriptionModel:
    """Test Subscription model."""

    def test_create_subscription(self, user, subscription_plan):
        sub = Subscription.objects.create(
            user=user,
            plan=subscription_plan,
            status=Subscription.Status.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )
        assert sub.status == 'active'
        assert sub.auto_renew is True
        assert sub.payment_provider == 'admin'
        assert str(sub).startswith(f'{user}')

    def test_expired_subscription(self, user, subscription_plan):
        sub = Subscription.objects.create(
            user=user,
            plan=subscription_plan,
            status=Subscription.Status.EXPIRED,
            expires_at=timezone.now() - timedelta(days=1),
        )
        assert sub.status == 'expired'

    def test_cancel_subscription(self, user, subscription_plan):
        sub = Subscription.objects.create(
            user=user,
            plan=subscription_plan,
            status=Subscription.Status.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )
        sub.status = Subscription.Status.CANCELED
        sub.canceled_at = timezone.now()
        sub.auto_renew = False
        sub.save()
        assert sub.status == 'canceled'
        assert sub.auto_renew is False

    def test_payment_providers(self):
        assert Subscription.PaymentProvider.APPSTORE == 'appstore'
        assert Subscription.PaymentProvider.PLAYSTORE == 'playstore'
        assert Subscription.PaymentProvider.ADMIN == 'admin'

    def test_subscription_ordering(self, user, subscription_plan):
        s1 = Subscription.objects.create(
            user=user, plan=subscription_plan,
            status='active', expires_at=timezone.now() + timedelta(days=30),
        )
        s2 = Subscription.objects.create(
            user=user, plan=subscription_plan,
            status='active', expires_at=timezone.now() + timedelta(days=60),
        )
        subs = Subscription.objects.all()
        assert subs[0] == s2  # Most recent first
        assert subs[1] == s1


# ===== API Tests =====

@pytest.mark.django_db
class TestSubscriptionAPI:
    """Test subscription API endpoints."""

    PLANS_URL = '/api/v1/subscriptions/plans/'
    MY_SUB_URL = '/api/v1/subscriptions/my/'
    START_URL = '/api/v1/subscriptions/start/'
    CANCEL_URL = '/api/v1/subscriptions/cancel/'
    PREMIUM_STATUS_URL = '/api/v1/subscriptions/premium-status/'

    def test_list_plans(self, api_client, subscription_plan, free_plan):
        response = api_client.get(self.PLANS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2

    def test_list_plans_unauthenticated(self, api_client):
        """Plans should be public."""
        response = api_client.get(self.PLANS_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_get_my_subscription_none(self, auth_client):
        response = auth_client.get(self.MY_SUB_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['subscription'] is None

    def test_start_subscription(self, auth_client, user, subscription_plan):
        """User should be able to start a premium subscription."""
        response = auth_client.post(self.START_URL, {
            'plan_type': 'premium_monthly',
            'payment_provider': 'admin',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'active'
        assert response.data['plan']['plan_type'] == 'premium_monthly'

        # User should become premium
        user.refresh_from_db()
        assert user.is_premium is True
        assert user.premium_expiry is not None

    def test_start_subscription_twice(self, auth_client, user, subscription_plan):
        """Starting second subscription should cancel the first."""
        auth_client.post(self.START_URL, {
            'plan_type': 'premium_monthly',
            'payment_provider': 'admin',
        }, format='json')
        response = auth_client.post(self.START_URL, {
            'plan_type': 'premium_monthly',
            'payment_provider': 'admin',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Subscription.objects.filter(user=user).count() == 2
        # First one should be canceled
        first_sub = Subscription.objects.filter(user=user).order_by('started_at').first()
        assert first_sub.status == 'canceled'

    def test_start_subscription_unauthenticated(self, api_client, subscription_plan):
        response = api_client.post(self.START_URL, {
            'plan_type': 'premium_monthly',
            'payment_provider': 'admin',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cancel_subscription(self, auth_client, user, subscription_plan):
        auth_client.post(self.START_URL, {'plan_type': 'premium_monthly', 'payment_provider': 'admin'}, format='json')
        response = auth_client.post(self.CANCEL_URL)
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.is_premium is False

    def test_cancel_no_subscription(self, auth_client):
        response = auth_client.post(self.CANCEL_URL)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_premium_status(self, auth_client, user, subscription_plan):
        """Check premium status before and after subscribing."""
        # Before
        response = auth_client.get(self.PREMIUM_STATUS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_premium'] is False

        # Subscribe
        auth_client.post(self.START_URL, {'plan_type': 'premium_monthly', 'payment_provider': 'admin'}, format='json')

        # After
        response = auth_client.get(self.PREMIUM_STATUS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_premium'] is True
        assert response.data['premium_expiry'] is not None
