import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Sizda config papkasi ichida settings.py turibdi
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# auctions ilovasidan routingni import qilamiz
from auctions.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
