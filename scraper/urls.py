from django.urls import path
from .views import MarketDataListView, MarketDataRetrieveView, login

urlpatterns = [
    path('login/', login, name='login'),
    path('marketdata/', MarketDataListView.as_view(), name='marketdata-list'),
    path('marketdata/<int:id>/', MarketDataRetrieveView.as_view(), name='marketdata-retrieve'),
]




# from django.urls import path
# from . import views

# urlpatterns = [
#     path('get-market-data/', views.get_market_data, name='get_market_data'),
# ]
