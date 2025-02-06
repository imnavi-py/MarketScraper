# serializers.py
from rest_framework import serializers
from .models import MarketData

class MarketDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketData
        fields = ['id', 'title', 'title_link', 'text', 'image_url', 'paragraphs', 'created_at']