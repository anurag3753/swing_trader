from django.shortcuts import render
from django_filters.views import FilterView
from .models import Signal
from .filters import SignalFilter
from django.db.models import F, Value, Subquery, OuterRef
from django.db.models.functions import Concat
from django.utils import timezone
from django.db.models import Case, When, BooleanField
from datetime import timedelta

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

        # Create a subquery to filter out duplicates
        unique_signals_subquery = Signal.objects.filter(
            symbol=OuterRef('symbol'),
            date=OuterRef('date'),
            buy_price=OuterRef('buy_price'),
            sell_price=OuterRef('sell_price')
        ).values('pk')[:1]

        queryset = queryset.annotate(
            unique_signal=Subquery(unique_signals_subquery)
        ).filter(pk=F('unique_signal'))

        # Get today's date
        today = timezone.now().date()

        # Create a subquery to filter out duplicates
        unique_signals_subquery = Signal.objects.filter(
            symbol=OuterRef('symbol'),
            date=OuterRef('date'),
            buy_price=OuterRef('buy_price'),
            sell_price=OuterRef('sell_price')
        ).values('pk')[:1]

        # Annotate with a flag for new stocks (added within the last 10 days)
        queryset = queryset.annotate(
            unique_signal=Subquery(unique_signals_subquery),
            is_new=Case(
                When(added_date__gte=today - timedelta(days=10), then=True),  # Check if added in the last 10 days
                default=False,
                output_field=BooleanField()
            )
        ).filter(pk=F('unique_signal'))

        for signal in queryset:
            print(signal.symbol, signal.added_date, signal.is_new)

        return queryset
