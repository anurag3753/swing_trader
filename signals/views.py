from django.shortcuts import render
from django_filters.views import FilterView
from .models import Signal
from .filters import SignalFilter

class SignalListView(FilterView):
    model = Signal
    template_name = 'signals/signals_list.html'
    filterset_class = SignalFilter
    context_object_name = 'signals'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Optionally, you can perform additional filtering or ordering here
        return queryset
