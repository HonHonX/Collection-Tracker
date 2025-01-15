from decouple import config
import requests
from django.shortcuts import render

api_key = config('TICKETMASTER_API_KEY')

def artist_events(request):
    artist_name = request.GET.get('artist', '') 
    events = []

    if artist_name:
        api_key = settings.TICKETMASTER_API_KEY
        base_url = 'https://app.ticketmaster.com/discovery/v2/events.json'
        
        params = {
            'keyword': artist_name,
            'apikey': api_key,
            # 'countryCode': 'DE'  # Optional: Filter auf ein Land, z. B. Deutschland
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if '_embedded' in data:
                events = data['_embedded'].get('events', [])

    return render(request, 'artist_events.html', {'events': events, 'artist': artist_name})
