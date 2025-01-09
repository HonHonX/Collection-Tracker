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


def get_more_artist_data(spotify_id, artist_name, user):
    """
    Fetch artist data along with their releases using the Discogs API with authentication.
    Results are cached for efficiency.
    """
    cache_key = f"artist_data_with_releases_{artist_name.lower()}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data

    try:
        # Perform an authenticated search using the application-level token
        artist_results = d.search(artist_name, type='artist', per_page=1)
        if not artist_results:
            raise IndexError("No artist found with the given name.")
        
        # Get the first matching artist
        artist = artist_results[0]

        # Extract artist details
        artist_details = {
            'id': artist.id,
            'profile': getattr(artist, 'profile', 'No profile available'),
            'aliases': [alias.name for alias in getattr(artist, 'aliases', [])],
            'members': [member.name for member in getattr(artist, 'members', [])],
            'urls': getattr(artist, 'urls', []),
        }

        # Save the artist details to the database
        with transaction.atomic():  # Use atomic transaction for data consistency
            artist_instance, created = Artist.objects.get_or_create(id=spotify_id, defaults={
                'name': artist_name,
                'photo_url': '',
                'popularity': 0,
            })
            artist_instance.discogs_id = artist_details['id']
            artist_instance.profile = artist_details['profile']
            artist_instance.set_aliases(artist_details['aliases'])
            artist_instance.set_members(artist_details['members'])
            artist_instance.set_urls(artist_details['urls'])
            artist_instance.save()

            # Set genres to an empty list if not provided
            artist_instance.set_genres([])

        # Cache the result for 1 hour
        result = {
            'discogs_id': artist_details['id'],
            'profile': artist_details['profile'],
            'aliases': artist_details['aliases'],
            'members': artist_details['members'],
            'urls': artist_details['urls'],
            'error': None,
        }
        cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour

        return result

    except Exception as e:
        return {'error': str(e)}
