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

        # Step 1: Get the IDs of records with highest sell_price for each symbol-buy_price combo
        max_sell_price_signal_ids = []
        symbol_buy_price_combos = queryset.values('symbol', 'buy_price').distinct()
        
        for combo in symbol_buy_price_combos:
            max_sell_price_signal = queryset.filter(
                symbol=combo['symbol'],
                buy_price=combo['buy_price']
            ).order_by('-sell_price').first()
            if max_sell_price_signal:
                max_sell_price_signal_ids.append(max_sell_price_signal.pk)

        # Filter queryset to only include the maximum sell price signals
        queryset = queryset.filter(pk__in=max_sell_price_signal_ids)

        # Step 2: If there are still multiple entries for same symbol-date, pick one with highest sell_price
        final_signal_ids = []
        symbol_date_combos = queryset.values('symbol', 'date').distinct()
        
        for combo in symbol_date_combos:
            best_signal = queryset.filter(
                symbol=combo['symbol'],
                date=combo['date']
            ).order_by('-sell_price', '-expected_gain').first()
            if best_signal:
                final_signal_ids.append(best_signal.pk)

        # Filter queryset to only include the final selected signals
        queryset = queryset.filter(pk__in=final_signal_ids)

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
