from django.urls import path
from . import views

urlpatterns = [
    path('safety-timers/', views.SafetyTimerListView.as_view(), name='safety-timers'),
    path('safety-timers/create/', views.CreateSafetyTimerView.as_view(), name='safety-timers-create'),
    path('safety-timers/<uuid:timer_id>/confirm/', views.ConfirmArrivalView.as_view(), name='safety-timers-confirm'),
    path('safety-timers/<uuid:timer_id>/cancel/', views.CancelSafetyTimerView.as_view(), name='safety-timers-cancel'),
]
