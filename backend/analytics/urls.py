from django.urls import path
from . import views

urlpatterns = [
    path('analytics/track/', views.TrackEventView.as_view(), name='analytics-track'),
    path('analytics/admin/dashboard/', views.AdminDashboardView.as_view(), name='analytics-dashboard'),
    path('analytics/admin/reports/', views.DailyReportListView.as_view(), name='analytics-reports'),
    path('analytics/admin/events/', views.AnalyticsEventListView.as_view(), name='analytics-events'),
]
