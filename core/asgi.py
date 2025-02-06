# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from scraper.consumers import MarketDataConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # این بخش برای درخواست‌های HTTP است
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/market_data/', MarketDataConsumer.as_asgi()),  # این بخش برای WebSocket است
        ])
    ),
})
