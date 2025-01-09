from decouple import config
import discogs_client
from django.core.cache import cache
from django.db import transaction
from collection.models import Artist, Album

# Retrieve application-level credentials from .env
DISCOGS_APP_NAME = config('DISCOGS_APP_NAME')
DISCOGS_CONSUMER_KEY = config('DISCOGS_CONSUMER_KEY')
DISCOGS_CONSUMER_SECRET = config('DISCOGS_CONSUMER_SECRET')
DISCOGS_ACCESS_TOKEN = config('DISCOGS_ACCESS_TOKEN')
DISCOGS_ACCESS_SECRET = config('DISCOGS_ACCESS_SECRET')

# Initialize the Discogs client with authentication
d = discogs_client.Client(
    DISCOGS_APP_NAME,
    consumer_key=DISCOGS_CONSUMER_KEY,
    consumer_secret=DISCOGS_CONSUMER_SECRET
)
d.set_token(DISCOGS_ACCESS_TOKEN, DISCOGS_ACCESS_SECRET)


def get_more_artist_data(artist_id, artist_name, user):
    """
    Fetch additional artist data from Discogs API.
    
    Args:
        artist_id (str): The Spotify ID of the artist.
        artist_name (str): The name of the artist.
        user (User): The user requesting the data.
    
    Returns:
        dict: A dictionary containing additional artist data.
    """
    cache_key = f"artist_data_with_releases_{artist_name.lower()}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data

    try:
        results = d.search(artist_name, type='artist')
        if results:
            artist = results[0]
            artist_details = {
                'discogs_id': artist.id,
                'profile': artist.profile,
            }

            # Save the artist details to the database
            with transaction.atomic():  # Use atomic transaction for data consistency
                artist_instance, created = Artist.objects.get_or_create(id=artist_id, defaults={
                    'name': artist_name,
                    'photo_url': '',
                    'popularity': 0,
                })
                artist_instance.discogs_id = artist_details['discogs_id']
                artist_instance.profile = artist_details['profile']
                artist_instance.save()

            # Cache the result for 1 hour
            cache.set(cache_key, artist_details, timeout=3600)  # Cache for 1 hour

            return artist_details

    except Exception as e:
        print(f"Error fetching data from Discogs: {e}")
    return {}
