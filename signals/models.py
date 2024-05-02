# signals/models.py
from django.db import models

class Signal(models.Model):
    symbol = models.CharField(max_length=20)
    date = models.DateField()
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    expected_gain = models.DecimalField(max_digits=5, decimal_places=2)
    strategy = models.CharField(max_length=100)  # Adjust max_length as needed
    universe = models.CharField(max_length=100)  # Add universe field

    def __str__(self):
        return f"{self.symbol} - Buy: {self.buy_price}, Sell: {self.sell_price}, Gain: {self.expected_gain}%"
