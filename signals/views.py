from django.shortcuts import render
from django_filters.views import FilterView
from .models import Signal
from .filters import SignalFilter
from django.db.models import F, Subquery, OuterRef, Case, When, BooleanField
from django.utils import timezone
from datetime import timedelta
import yfinance as yf

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

        # Get today's date
        today = timezone.now().date()

        # Create a subquery to filter out duplicates
        unique_signals_subquery = Signal.objects.filter(
            symbol=OuterRef('symbol'),
            date=OuterRef('date'),
            buy_price=OuterRef('buy_price'),
            sell_price=OuterRef('sell_price')
        ).values('pk')[:1]

        # Annotate with a flag for new stocks (added within the last 7 days)
        queryset = queryset.annotate(
            unique_signal=Subquery(unique_signals_subquery),
            is_new=Case(
                When(added_date__gte=today - timedelta(days=7), then=True),  # Check if added in the last 7 days
                default=False,
                output_field=BooleanField()
            )
        ).filter(pk=F('unique_signal'))

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
                price_change_percentage = round(((current_price - float(signal.buy_price)) / float(signal.buy_price)) * 100, 2)
                signal.price_change_percentage = price_change_percentage
            else:
                signal.price_change_percentage = None

            # Format the date to YYYY-MM-DD
            signal.date = signal.date.strftime('%Y-%m-%d')

        return context
