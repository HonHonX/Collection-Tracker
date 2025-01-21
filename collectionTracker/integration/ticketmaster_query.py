from decouple import config
import requests
from django.http import JsonResponse

api_key = config('TICKETMASTER_API_KEY')

def fetch_artist_events(request, artist_name):
    """
    Fetch events for a given artist from the Ticketmaster API.

    Args:
        request (HttpRequest): The HTTP request object.
        artist_name (str): The name of the artist to search for events.
        This function has been created with the help of the Ticketmaster API documentation and AI.

    Returns:
        JsonResponse: A JSON response containing a list of events for the artist.
    """
    events = []

    if (artist_name):
        base_url = 'https://app.ticketmaster.com/discovery/v2/events.json'
        
        params = {
            'keyword': artist_name,  
            'apikey': api_key,       
            'size': 10,       
            'classificationName': 'music'        
        }
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if '_embedded' in data:
                events = data['_embedded'].get('events', [])
                
                for event in events:
                    venues = event.get('_embedded', {}).get('venues', [])
                    if venues:
                        venue = venues[0]
                        event['coordinates'] = {
                            'latitude': venue.get('location', {}).get('latitude'),
                            'longitude': venue.get('location', {}).get('longitude')
                        }
                        event['address'] = venue.get('address', {}).get('line1')
                        event['city'] = venue.get('city', {}).get('name')
                        event['state'] = venue.get('state', {}).get('stateCode') if venue.get('state', {}).get('stateCode') else None
                        event['country'] = venue.get('country', {}).get('countryCode')
                    
                    start_time = event.get('dates', {}).get('start', {}).get('localTime')
                    if start_time:
                        event['start_time'] = start_time[:5]
                    else:
                        event['start_time'] = None
                    event['start_date'] = event.get('dates', {}).get('start', {}).get('localDate')
                    event['timezone'] = event.get('dates', {}).get('timezone')
                    event['image'] = event.get('images', [])[0].get('url') if event.get('images') else None
                    event['url'] = event.get('url') if event.get('url') else None

    return JsonResponse({'events': events})
