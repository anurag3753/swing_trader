from django.urls import path
from .views import StockSignalListView

urlpatterns = [
    path('', StockSignalListView.as_view(), name='stock_signals'),
]
