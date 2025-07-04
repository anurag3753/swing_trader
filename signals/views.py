from django.shortcuts import render
from django_filters.views import FilterView
from .models import Signal
from .filters import SignalFilter
from django.db.models import F, Subquery, OuterRef, Case, When, BooleanField, Max
from django.utils import timezone
from datetime import timedelta
from core.mixins import LTHFilterMixin
import yfinance as yf

class SignalListView(LTHFilterMixin, FilterView):
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

        # Get today's date
        today = timezone.now().date()

        # Get the IDs of records with max sell_price for each symbol-buy_price combo
        max_profit_signal_ids = []
        symbol_buy_price_combos = queryset.values('symbol', 'buy_price').distinct()
        
        for combo in symbol_buy_price_combos:
            max_signal = queryset.filter(
                symbol=combo['symbol'],
                buy_price=combo['buy_price']
            ).order_by('-sell_price').first()
            if max_signal:
                max_profit_signal_ids.append(max_signal.pk)

        # Filter queryset to only include the max profit signals
        queryset = queryset.filter(pk__in=max_profit_signal_ids)

        # Annotate with a flag for new stocks (added within the last 7 days)
        queryset = queryset.annotate(
            is_new=Case(
                When(added_date__gte=today - timedelta(days=7), then=True),
                default=False,
                output_field=BooleanField()
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signals = list(context['signals'])
        
        # Use the mixin to add LTH data and filtering
        filtered_signals = self.add_lth_data_to_signals(signals, price_field='buy_price')
        
        # Update context with filtered signals and LTH info
        context['signals'] = filtered_signals
        context = self.add_lth_context(context, signals, filtered_signals)

        return context
