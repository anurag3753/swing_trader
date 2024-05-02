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
        # Get the query parameters
        strategy = self.request.GET.get('strategy')
        universe = self.request.GET.get('universe')
        
        # Optionally, perform additional filtering based on the query parameters
        if strategy:
            queryset = queryset.filter(strategy=strategy)
        if universe:
            queryset = queryset.filter(universe=universe)

        return queryset
