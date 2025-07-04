# signals/models.py
from django.db import models
from django.utils import timezone

class Signal(models.Model):
    symbol = models.CharField(max_length=20)
    date = models.DateField()
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    expected_gain = models.DecimalField(max_digits=5, decimal_places=2)
    strategy = models.CharField(max_length=100)  # Adjust max_length as needed
    universe = models.CharField(max_length=100)  # Add universe field
    added_date = models.DateField(default=timezone.now)  # Date when the record is added

    def __str__(self):
        return f"{self.symbol} - Buy: {self.buy_price}, Sell: {self.sell_price}, Gain: {self.expected_gain}%"

    def get_lth_data(self):
        """Get LTH data for this signal's symbol."""
        from core.utils import LTHHelper
        return LTHHelper.get_lth_data(self.symbol)

    def get_distance_from_lth(self):
        """Get distance from LTH using buy_price."""
        from core.utils import LTHHelper
        return LTHHelper.calculate_distance_from_lth(self.buy_price, self.symbol)

    def is_near_lth(self, threshold_pct=10.0):
        """Check if buy_price is near LTH."""
        from core.utils import LTHHelper
        return LTHHelper.is_near_lth(self.buy_price, self.symbol, threshold_pct)
