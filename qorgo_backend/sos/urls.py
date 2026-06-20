from django.urls import path
from . import views

urlpatterns = [
    path('alerts/', views.AlertListView.as_view(), name='alerts-list'),
    path('alerts/create/', views.CreateAlertView.as_view(), name='alerts-create'),
    path('alerts/<uuid:pk>/', views.AlertDetailView.as_view(), name='alerts-detail'),
    path('alerts/<uuid:alert_id>/resolve/', views.ResolveAlertView.as_view(), name='alerts-resolve'),
    path('alerts/<uuid:alert_id>/evidence/', views.AlertEvidenceListView.as_view(), name='alerts-evidence'),
    path('alerts/<uuid:alert_id>/evidence/upload/', views.UploadEvidenceView.as_view(), name='alerts-evidence-upload'),
]
