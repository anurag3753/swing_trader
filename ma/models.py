from django.db import models

class StockSignal(models.Model):
    symbol = models.CharField(max_length=20)
    date = models.DateField()
    action = models.CharField(max_length=4)  # 'buy' or 'sell'
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.symbol} - Price: {self.price}, Action: {self.action}"