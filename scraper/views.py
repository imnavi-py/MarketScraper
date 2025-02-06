from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework import generics
from .models import MarketData
from .serializers import MarketDataSerializer

@api_view(['POST'])
def login(request):

    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key
        })
    else:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class MarketDataListView(generics.ListAPIView):
    serializer_class = MarketDataSerializer
    def get_queryset(self):
        queryset = MarketData.objects.all()
        title = self.request.query_params.get('title', None)
        
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

class MarketDataRetrieveView(generics.RetrieveAPIView):
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    lookup_field = 'id'

class MarketDataDeleteView(generics.DestroyAPIView):
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    lookup_field = 'id'





