import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket for real-time notifications to a specific user."""

    async def connect(self):
        self.user = None

        # Authenticate via JWT token
        token_key = self.scope['query_string'].decode().split('token=')[-1] if 'token=' in self.scope['query_string'].decode() else None

        if token_key:
            try:
                access_token = AccessToken(token_key)
                user_id = access_token['user_id']
                self.user = await database_sync_to_async(User.objects.get)(id=user_id)
            except Exception:
                await self.close(code=4001)
                return
        else:
            await self.close(code=4001)
            return

        # Create personal notification group
        self.notification_group = f'user_{self.user.id}_notifications'
        await self.channel_layer.group_add(
            self.notification_group,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group'):
            await self.channel_layer.group_discard(
                self.notification_group,
                self.channel_name,
            )

    async def receive(self, text_data):
        """Handle incoming messages (e.g., mark as read)."""
        try:
            data = json.loads(text_data)
            if data.get('action') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except Exception:
            pass

    async def send_notification(self, event):
        """Send notification to WebSocket client."""
        await self.send(text_data=json.dumps(event))
