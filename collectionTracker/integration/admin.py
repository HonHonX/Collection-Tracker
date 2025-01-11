from django.contrib import admin
from .models import DailyExchangeRate

# Register the DailyExchangeRate model with the admin panel
@admin.register(DailyExchangeRate)
class DailyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('date', 'usd_to_eur')
    search_fields = ('date',)
    list_filter = ('date',)