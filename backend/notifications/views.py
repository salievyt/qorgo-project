from common.schema import MessageSerializer, NotificationInputSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import inline_serializer, extend_schema

from .services import send_push_notification


@extend_schema(summary='Test push notification (dev only)', tags=['Notifications'])
class TestNotificationView(APIView):
    @extend_schema(request=NotificationInputSerializer, responses=MessageSerializer)
    def post(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Staff only.'}, status=status.HTTP_403_FORBIDDEN)

        title = request.data.get('title', 'Test Notification')
        body = request.data.get('body', 'This is a test notification from Qorgo.')

        send_push_notification(request.user, title, body, {'type': 'test'})
        return Response({'message': 'Test notification sent.'})
