import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class LocationConsumer(AsyncWebsocketConsumer):
    """WebSocket for real-time location updates within families."""

    async def connect(self):
        self.user = None

        # Authenticate via JWT token in query string
        token_key = self.scope['query_string'].decode().split('token=')[-1] if 'token=' in self.scope['query_string'].decode() else None

        if token_key:
            try:
                access_token = AccessToken(token_key)
                user_id = access_token['user_id']
                self.user = await database_sync_to_async(User.objects.get)(id=user_id)
            except Exception as e:
                await self.close(code=4001)
                return
        else:
            await self.close(code=4001)
            return

        # Join user's family groups
        self.family_ids = await self.get_user_family_ids()

        for family_id in self.family_ids:
            await self.channel_layer.group_add(
                f'family_{family_id}',
                self.channel_name,
            )

        await self.accept()

    async def disconnect(self, close_code):
        for family_id in getattr(self, 'family_ids', []):
            await self.channel_layer.group_discard(
                f'family_{family_id}',
                self.channel_name,
            )

    async def receive(self, text_data):
        """Receive location update and broadcast to family members."""
        try:
            data = json.loads(text_data)
            location_data = {
                'type': 'location_update',
                'user_id': str(self.user.id),
                'user_name': f'{self.user.first_name} {self.user.last_name}',
                'photo': self.user.photo.url if self.user.photo else None,
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'speed': data.get('speed', 0),
                'battery_level': data.get('battery_level', 100),
                'accuracy': data.get('accuracy', 0),
                'timestamp': data.get('timestamp', ''),
            }

            # Broadcast to all family groups
            for family_id in self.family_ids:
                await self.channel_layer.group_send(
                    f'family_{family_id}',
                    location_data,
                )

            # Save to DB
            from location.models import LocationUpdate, ActiveLocation
            await database_sync_to_async(LocationUpdate.objects.create)(
                user=self.user,
                latitude=data.get('latitude', 0),
                longitude=data.get('longitude', 0),
                accuracy=data.get('accuracy', 0),
                speed=data.get('speed', 0),
                battery_level=data.get('battery_level', 100),
                is_background=data.get('is_background', False),
            )
            await database_sync_to_async(
                lambda: ActiveLocation.objects.update_or_create(
                    user=self.user,
                    defaults={
                        'latitude': data['latitude'],
                        'longitude': data['longitude'],
                        'accuracy': data.get('accuracy', 0),
                        'speed': data.get('speed', 0),
                        'battery_level': data.get('battery_level', 100),
                        'is_stale': False,
                    }
                )
            )()

        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def location_update(self, event):
        """Send location update to WebSocket client."""
        await self.send(text_data=json.dumps(event))

    async def family_notification(self, event):
        """Send family notification through WebSocket."""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user_family_ids(self):
        from families.models import Family
        return list(Family.objects.filter(
            members=self.user
        ).values_list('id', flat=True))
