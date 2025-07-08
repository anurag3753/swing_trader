"""Utility functions for working with LTH data across apps."""

from core.models import StockLTH


class LTHHelper:
    """Helper class for LTH-related operations."""
    
    @staticmethod
    def get_lth_price(symbol):
        """Get LTH price for a symbol."""
        return StockLTH.get_lth_price(symbol)
    
    @staticmethod
    def get_lth_data(symbol):
        """Get complete LTH data for a symbol."""
        try:
            stock_lth = StockLTH.objects.get(symbol=symbol)
            return {
                'lth_price': stock_lth.lth_price,
                'lth_date': stock_lth.lth_date,
                'universe': stock_lth.universe,
                'last_updated': stock_lth.last_updated
            }
        except StockLTH.DoesNotExist:
            return None
    
    @staticmethod
    def calculate_distance_from_lth(current_price, symbol):
        """Calculate percentage distance from LTH."""
        lth_price = LTHHelper.get_lth_price(symbol)
        if lth_price is None:
            return None
        
        distance_pct = ((float(lth_price) - float(current_price)) / float(lth_price)) * 100
        return round(distance_pct, 2)
    
    @staticmethod
    def is_near_lth(current_price, symbol, threshold_pct=5.0):
        """Check if current price is within threshold percentage of LTH."""
        distance = LTHHelper.calculate_distance_from_lth(current_price, symbol)
        if distance is None:
            return None
        
        return abs(distance) <= threshold_pct
    
    @staticmethod
    def get_lth_bulk(symbols):
        """Get LTH data for multiple symbols efficiently."""
        lth_data = {}
        queryset = StockLTH.objects.filter(symbol__in=symbols)
        
        for stock_lth in queryset:
            lth_data[stock_lth.symbol] = {
                'lth_price': stock_lth.lth_price,
                'lth_date': stock_lth.lth_date,
                'universe': stock_lth.universe,
                'last_updated': stock_lth.last_updated
            }
        
        return lth_data

    @staticmethod
    def update_lth_from_quotes(stock_quotes, universe=None):
        """
        Update LTH data from existing stock quotes data.
        This is useful during strategy processing to avoid duplicate API calls.
        
        Args:
            stock_quotes: Dictionary of {symbol: DataFrame} with stock data
            universe: Universe/category name for the stocks
        
        Returns:
            Dictionary with update statistics
        """
        updated_count = 0
        new_count = 0
        error_count = 0
        
        for symbol, data in stock_quotes.items():
            try:
                if data.empty:
                    continue
                
                # Find the highest closing price and its date
                max_close_idx = data['Close'].idxmax()
                lth_price = data.loc[max_close_idx, 'Close']
                lth_date = max_close_idx.date()
                
                # Update or create LTH record
                was_updated_or_new = StockLTH.update_lth_if_higher(
                    symbol=symbol,
                    price=lth_price,
                    date=lth_date,
                    universe=universe
                )
                
                if was_updated_or_new:
                    # Check if it's a new record or an update
                    existing_records = StockLTH.objects.filter(symbol=symbol).count()
                    if existing_records == 1:
                        new_count += 1
                    else:
                        updated_count += 1
                        
            except Exception as e:
                error_count += 1
                print(f"Error updating LTH for {symbol}: {str(e)}")
        
        return {
            'updated': updated_count,
            'new': new_count,
            'errors': error_count,
            'total_processed': len(stock_quotes)
        }
