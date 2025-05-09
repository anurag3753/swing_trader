from django.views.generic import ListView
from django.db.models import F, Subquery, OuterRef, Case, When, BooleanField
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

        # Create a subquery to filter out duplicates
        unique_signals_subquery = StockSignal.objects.filter(
            symbol=OuterRef('symbol'),
            date=OuterRef('date'),
            price=OuterRef('price'),
        ).values('pk')[:1]

        # Annotate the queryset with the unique signal and a flag for new signals
        queryset = queryset.annotate(
            unique_signal=Subquery(unique_signals_subquery),
            is_new=Case(
                When(date__gte=today - timedelta(days=7), then=True),  # Check if added in the last 7 days
                default=False,
                output_field=BooleanField()
            )
        ).filter(pk=F('unique_signal'))

        # Cache for storing fetched prices
        price_cache = {}

        # Fetch current market price for each stock signal and calculate percentage change
        for signal in queryset:
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

        return queryset
