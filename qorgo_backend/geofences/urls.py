from django.urls import path
from . import views

urlpatterns = [
    path('geofences/', views.GeofenceListView.as_view(), name='geofences-list'),
    path('geofences/<uuid:pk>/', views.GeofenceDetailView.as_view(), name='geofences-detail'),
    path('geofences/events/', views.GeofenceEventListView.as_view(), name='geofence-events'),
]
