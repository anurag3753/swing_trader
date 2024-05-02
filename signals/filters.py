import django_filters
from .models import Signal

class SignalFilter(django_filters.FilterSet):
    class Meta:
        model = Signal
        fields = ['strategy', 'universe']  # Add more fields as needed
