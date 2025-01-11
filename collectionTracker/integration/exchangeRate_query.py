from decouple import config
import requests

def usd_to_eur(usd_amount):

    key = config('EXCHANGE_RATE_API_KEY')
    api_url = f"https://v6.exchangerate-api.com/v6/{key}/latest/USD"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            eur_rate = data['conversion_rates']['EUR']
            # Convert the USD amount to EUR.
            eur_amount = usd_amount * eur_rate
            eur_amount = round(eur_amount, 2)
            return eur_amount
        else:
            print(f"Error: Unable to fetch exchange rate. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None