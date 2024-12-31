from django.views.generic import ListView
from django.db.models import F, Subquery, OuterRef, Case, When, BooleanField
from django.utils import timezone
from datetime import timedelta
from .models import StockSignal

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
                When(date__gte=today - timedelta(days=7), then=True),  # Check if added in the last 3 days
                default=False,
                output_field=BooleanField()
            )
        ).filter(pk=F('unique_signal'))

        return queryset
