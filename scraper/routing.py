# routing.py
from django.urls import path
from .consumers import MarketDataConsumer

websocket_urlpatterns = [
    path("ws/market_data/", MarketDataConsumer.as_asgi()),
]
