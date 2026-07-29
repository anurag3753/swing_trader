from django.urls import path
from .views import StockSignalListView

urlpatterns = [
    path('', StockSignalListView.as_view(), name='stock_signals'),
    path('us/', StockSignalListView.as_view(us=True, filter_signals=False), name='stock_signals_us'),
]
