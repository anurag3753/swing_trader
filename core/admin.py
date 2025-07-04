from django.contrib import admin
from .models import StockLTH


@admin.register(StockLTH)
class StockLTHAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'lth_price', 'lth_date', 'universe', 'last_updated']
    list_filter = ['universe', 'lth_date', 'last_updated']
    search_fields = ['symbol']
    readonly_fields = ['last_updated']
    ordering = ['-lth_price']
