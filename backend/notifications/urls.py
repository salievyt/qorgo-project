from django.urls import path
from . import views

urlpatterns = [
    path('notifications/test/', views.TestNotificationView.as_view(), name='notifications-test'),
]
