from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price_usd', 'price_som', 'max_family_members', 'is_active')
    list_filter = ('plan_type', 'is_active')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'started_at', 'expires_at', 'auto_renew')
    list_filter = ('status', 'plan', 'payment_provider')
    search_fields = ('user__phone_number',)
