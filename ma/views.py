from django.views.generic import ListView
from django.db.models import F, Subquery, OuterRef, Case, When, BooleanField, Min
from django.utils import timezone
from datetime import timedelta
from .models import StockSignal
import yfinance as yf

class StockSignalListView(ListView):
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
        signals = context['signals']
        
        # Cache for storing fetched prices
        price_cache = {}

        # Fetch current market price for each stock signal and calculate percentage change
        for signal in signals:
            if signal.symbol not in price_cache:
                ticker = yf.Ticker(signal.symbol)
                try:
                    current_price = round(ticker.history(period="1d")['Close'].iloc[-1], 2)
                    price_cache[signal.symbol] = current_price
                except Exception as e:
                    price_cache[signal.symbol] = None
                    print(f"Failed to fetch current price for {signal.symbol}: {e}")

            current_price = price_cache[signal.symbol]
            if current_price is not None:
                price_change_percentage = round(((current_price - float(signal.price)) / float(signal.price)) * 100, 2)
                signal.price_change_percentage = price_change_percentage
            else:
                signal.price_change_percentage = None

            # Format the date to YYYY-MM-DD
            signal.date = signal.date.strftime('%Y-%m-%d')

        return context
