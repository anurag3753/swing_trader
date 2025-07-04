from django.views.generic import ListView
from django.db.models import F, Subquery, OuterRef, Case, When, BooleanField, Min
from django.utils import timezone
from datetime import timedelta
from .models import StockSignal
from core.mixins import LTHFilterMixin
import yfinance as yf

class StockSignalListView(LTHFilterMixin, ListView):
    model = StockSignal
    template_name = 'ma/stock_signals.html'
    context_object_name = 'signals'
    ordering = ['date']

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', 'date')
        return ordering
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Get today's date
        today = timezone.now().date()

        # Get the IDs of records with minimum price for each symbol
        lowest_price_signal_ids = []
        unique_symbols = queryset.values('symbol').distinct()
        
        for symbol_dict in unique_symbols:
            symbol = symbol_dict['symbol']
            lowest_price_signal = queryset.filter(
                symbol=symbol
            ).order_by('price').first()
            if lowest_price_signal:
                lowest_price_signal_ids.append(lowest_price_signal.pk)

        # Filter queryset to only include the lowest price signals
        queryset = queryset.filter(pk__in=lowest_price_signal_ids)

        # Annotate with a flag for new signals (added within the last 7 days)
        queryset = queryset.annotate(
            is_new=Case(
                When(date__gte=today - timedelta(days=7), then=True),
                default=False,
                output_field=BooleanField()
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signals = list(context['signals'])
        
        # Use the mixin to add LTH data and filtering
        filtered_signals = self.add_lth_data_to_signals(signals, price_field='price')
        
        # Update context with filtered signals and LTH info
        context['signals'] = filtered_signals
        context = self.add_lth_context(context, signals, filtered_signals)
        
        return context
