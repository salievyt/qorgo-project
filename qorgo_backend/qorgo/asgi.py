"""
ASGI config for Qorgo project.
Supports WebSocket connections for real-time location sharing and notifications.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qorgo.settings')

django_asgi_app = get_asgi_application()

from location.routing import websocket_urlpatterns as location_websockets
from notifications.routing import websocket_urlpatterns as notification_websockets

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                location_websockets + notification_websockets
            )
        )
    ),
})
