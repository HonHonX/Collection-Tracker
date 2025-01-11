from django.db import models

class DailyExchangeRate(models.Model):
    date = models.DateField(unique=True)
    usd_to_eur = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: USD to EUR = {self.usd_to_eur}"