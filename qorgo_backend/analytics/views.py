from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import AnalyticsEvent, DailyReport
from .serializers import AnalyticsEventSerializer, DailyReportSerializer
from accounts.models import User
from sos.models import Alert
from families.models import Family


@extend_schema(summary='Track analytics event', tags=['Analytics'])
class TrackEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        event_name = request.data.get('event_name')
        parameters = request.data.get('parameters', {})

        if not event_name:
            return Response({'error': 'Event name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        AnalyticsEvent.objects.create(
            user=request.user,
            event_name=event_name,
            session_id=request.data.get('session_id'),
            parameters=parameters,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )

        return Response({'success': True})


@extend_schema(summary='Get admin dashboard stats', tags=['Analytics'])
class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = timezone.now()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)

        return Response({
            'total_users': User.objects.filter(is_deleted=False).count(),
            'new_users_today': User.objects.filter(date_joined__date=today.date()).count(),
            'new_users_7days': User.objects.filter(date_joined__gte=last_7_days).count(),
            'new_users_30days': User.objects.filter(date_joined__gte=last_30_days).count(),
            'active_users_today': User.objects.filter(last_active_at__gte=last_30_days).count(),
            'premium_users': User.objects.filter(is_premium=True).count(),
            'total_alerts': Alert.objects.count(),
            'active_alerts': Alert.objects.filter(status='active').count(),
            'alerts_today': Alert.objects.filter(started_at__date=today.date()).count(),
            'alerts_7days': Alert.objects.filter(started_at__gte=last_7_days).count(),
            'total_families': Family.objects.count(),
            'families_today': Family.objects.filter(created_at__date=today.date()).count(),
            'total_reports': DailyReport.objects.count(),
        })


@extend_schema(summary='List daily reports', tags=['Analytics'])
class DailyReportListView(generics.ListAPIView):
    queryset = DailyReport.objects.all().order_by('-date')[:90]
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(summary='Get apps analytics events', tags=['Analytics'])
class AnalyticsEventListView(generics.ListAPIView):
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return AnalyticsEvent.objects.all().order_by('-timestamp')[:100]
