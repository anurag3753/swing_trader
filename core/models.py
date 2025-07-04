from django.db import models
from django.utils import timezone


class StockLTH(models.Model):
    """Model to store Life Time High (LTH) closing prices for stocks."""
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    lth_price = models.DecimalField(max_digits=15, decimal_places=4)
    lth_date = models.DateField()
    last_updated = models.DateTimeField(default=timezone.now)
    universe = models.CharField(max_length=100, blank=True, null=True)  # Track which universe this stock belongs to
    
    class Meta:
        db_table = 'core_stock_lth'
        verbose_name = 'Stock Life Time High'
        verbose_name_plural = 'Stock Life Time Highs'
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['universe']),
        ]

    def __str__(self):
        return f"{self.symbol} - LTH: {self.lth_price} on {self.lth_date}"

    @classmethod
    def get_lth_price(cls, symbol):
        """Quick method to get LTH price for a symbol."""
        try:
            stock_lth = cls.objects.get(symbol=symbol)
            return stock_lth.lth_price
        except cls.DoesNotExist:
            return None

    @classmethod
    def update_lth_if_higher(cls, symbol, price, date, universe=None):
        """Update LTH if the provided price is higher than current LTH."""
        stock_lth, created = cls.objects.get_or_create(
            symbol=symbol,
            defaults={
                'lth_price': price,
                'lth_date': date,
                'universe': universe
            }
        )
        
        if not created and price > stock_lth.lth_price:
            stock_lth.lth_price = price
            stock_lth.lth_date = date
            stock_lth.last_updated = timezone.now()
            if universe:
                stock_lth.universe = universe
            stock_lth.save()
            return True  # LTH was updated
        elif not created:
            # Update last_updated timestamp even if LTH wasn't updated
            stock_lth.last_updated = timezone.now()
            if universe and not stock_lth.universe:
                stock_lth.universe = universe
            stock_lth.save()
        
        return created  # True if new record was created
