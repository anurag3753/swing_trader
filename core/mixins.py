"""
Shared mixins for LTH (Life Time High) functionality.
"""
from core.utils import LTHHelper
import yfinance as yf


class LTHFilterMixin:
    """Mixin to add LTH filtering and data to views."""
    
    def add_lth_data_to_signals(self, signals, price_field='price', filter_signals=True):
        """
        Add LTH data and optionally filter signals.
        
        Args:
            signals: QuerySet or list of signal objects
            price_field: Field name to use for price comparison (default: 'price')
            filter_signals: Whether to only return signals at least 20% below LTH.
        
        Returns:
            Signals with LTH data attached; filtered if requested.
        """
        # Cache for storing fetched prices
        price_cache = {}
        
        # Get all symbols for bulk LTH lookup
        symbols = [signal.symbol for signal in signals]
        lth_data = LTHHelper.get_lth_bulk(symbols)

        filtered_signals = []
        
        for signal in signals:
            # Fetch current market price
            if signal.symbol not in price_cache:
                ticker = yf.Ticker(signal.symbol)
                try:
                    current_price = round(ticker.history(period="1d")['Close'].iloc[-1], 2)
                    price_cache[signal.symbol] = current_price
                except Exception as e:
                    price_cache[signal.symbol] = None
                    print(f"Failed to fetch current price for {signal.symbol}: {e}")

            current_price = price_cache[signal.symbol]
            
            # Calculate price change percentage based on the specified field
            if current_price is not None:
                signal_price = getattr(signal, price_field)
                price_change_percentage = round(((current_price - float(signal_price)) / float(signal_price)) * 100, 2)
                signal.price_change_percentage = price_change_percentage
            else:
                signal.price_change_percentage = None

            # Add LTH data
            signal.lth_data = lth_data.get(signal.symbol)
            if signal.lth_data and current_price is not None:
                signal.distance_from_lth = LTHHelper.calculate_distance_from_lth(current_price, signal.symbol)
                signal.is_near_lth = LTHHelper.is_near_lth(current_price, signal.symbol, threshold_pct=10.0)

                if filter_signals:
                    # Filter: Only include stocks that are at least 20% below LTH
                    if signal.distance_from_lth <= -20.0:
                        filtered_signals.append(signal)
                else:
                    filtered_signals.append(signal)
            else:
                signal.distance_from_lth = None
                signal.is_near_lth = None
                if not filter_signals:
                    filtered_signals.append(signal)
                # If no LTH data available and filtering is enabled, skip this signal

            # Format the date to YYYY-MM-DD
            if hasattr(signal, 'date'):
                signal.date = signal.date.strftime('%Y-%m-%d')

        return filtered_signals

    def add_lth_context(self, context, original_signals, filtered_signals):
        """Add LTH-related context variables."""
        context['total_signals_before_filter'] = len(original_signals)
        context['total_signals_after_filter'] = len(filtered_signals)
        context['lth_filter_threshold'] = 20.0  # 20% below LTH threshold
        return context
