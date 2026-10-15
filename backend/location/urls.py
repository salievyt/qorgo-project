from django.urls import path
from . import views

urlpatterns = [
    path('operator/locations/', views.OperatorLocationsView.as_view(), name='operator-locations'),
    path('location/update/', views.UpdateLocationView.as_view(), name='location-update'),
    path('location/me/', views.MyLocationView.as_view(), name='location-me'),
    path('location/history/', views.LocationHistoryView.as_view(), name='location-history'),
    path('families/<uuid:family_id>/locations/', views.FamilyLocationsView.as_view(), name='family-locations'),
]
