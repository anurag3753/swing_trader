# signals/urls.py
from django.urls import path
from .views import SignalListView

urlpatterns = [
    path('', SignalListView.as_view(), name='signals_list'),
]

