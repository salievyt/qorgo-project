from django.urls import path
from . import views

urlpatterns = [
    path('subscriptions/plans/', views.SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('subscriptions/my/', views.MySubscriptionView.as_view(), name='my-subscription'),
    path('subscriptions/start/', views.StartSubscriptionView.as_view(), name='start-subscription'),
    path('subscriptions/cancel/', views.CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('subscriptions/premium-status/', views.PremiumStatusView.as_view(), name='premium-status'),
]
