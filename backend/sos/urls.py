from django.urls import path
from . import views

urlpatterns = [
    path('operator/incidents/', views.OperatorIncidentListView.as_view(), name='operator-incidents'),
    path('operator/incidents/<str:pk>/', views.OperatorIncidentDetailView.as_view(), name='operator-incident-detail'),
    path('operator/incidents/<str:alert_id>/take/', views.OperatorTakeIncidentView.as_view(), name='operator-incident-take'),
    path('operator/incidents/<str:alert_id>/close/', views.OperatorCloseIncidentView.as_view(), name='operator-incident-close'),
    path('alerts/', views.AlertListView.as_view(), name='alerts-list'),
    path('alerts/create/', views.CreateAlertView.as_view(), name='alerts-create'),
    path('alerts/<uuid:pk>/', views.AlertDetailView.as_view(), name='alerts-detail'),
    path('alerts/<uuid:alert_id>/resolve/', views.ResolveAlertView.as_view(), name='alerts-resolve'),
    path('alerts/<uuid:alert_id>/evidence/', views.AlertEvidenceListView.as_view(), name='alerts-evidence'),
    path('alerts/<uuid:alert_id>/evidence/upload/', views.UploadEvidenceView.as_view(), name='alerts-evidence-upload'),
]
