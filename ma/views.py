from django.views.generic import ListView
from .models import StockSignal

class StockSignalListView(ListView):
    model = StockSignal
    template_name = 'ma/stock_signals.html'
    context_object_name = 'signals'
    ordering = ['date']

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', 'date')
        return ordering