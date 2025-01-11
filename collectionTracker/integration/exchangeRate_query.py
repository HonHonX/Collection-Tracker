from decouple import config
import requests
from django.utils import timezone
from .models import DailyExchangeRate
import os
import django
from datetime import datetime

def fetch_and_save_usd_to_eur():
    """
    Fetch the current USD to EUR exchange rate and save it to the database.
    Return the fetched exchange rate.
    """
    api_key = config('EXCHANGE_RATE_API_KEY')
    url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}"
    response = requests.get(url)
    data = response.json()
    usd_to_eur = data['rates']['EUR']

    exchange_rate, created = DailyExchangeRate.objects.get_or_create(
        date=datetime.now().date(),
        defaults={'usd_to_eur': usd_to_eur}
    )
    if not created:
        exchange_rate.usd_to_eur = usd_to_eur
        exchange_rate.save()

    return float(usd_to_eur)

def usd_to_eur(usd_amount):
    """
    Convert USD amount to EUR using the latest exchange rate.
    """
    today = datetime.now().date()
    latest_rate = DailyExchangeRate.objects.filter(date=today).first()
    if not latest_rate:
        latest_rate = fetch_and_save_usd_to_eur()
    else:
        latest_rate = float(latest_rate.usd_to_eur)

    price = usd_amount * latest_rate if latest_rate else None

    return price
