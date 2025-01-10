from decouple import config
import discogs_client
from django.core.cache import cache
from django.db import transaction
from collection.models import Artist, Album
import bleach
import re

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

def format_string(string):
    """
    Format the string by removing the [] and the l= and a= parts, handling additional formatting,
    and removing round brackets with only numbers inside.

    Args:
        string (str): The original string.

    Returns:
        str: The formatted string.
    """
    # Remove round brackets with only numbers inside
    formatted_string = re.sub(r'\(\d+\)', '', string)
    
    # Replace [b] and [/b] with <strong> and </strong>
    formatted_string = re.sub(r'\[b\]', '', formatted_string)
    formatted_string = re.sub(r'\[/b\]', '', formatted_string)

    # Remove the [m= parts and the surrounding brackets, replacing with "their album"
    formatted_string = re.sub(r'\[m=\d+\]', 'release X', formatted_string)

    # Remove the [l= and [a= parts and the surrounding brackets
    formatted_string = re.sub(r'\[l=|\[a=|\]', '', formatted_string)
    
    return formatted_string

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
    cache_key = f"artist_data_with_releases_{artist_name.lower().strip()}"
    cached_data = cache.get(cache_key)
    
    if (cached_data):
        return cached_data

    try:
        results = d.search(artist_name, type='artist', per_page=15, page=1, exact=True)
        if (results):
            artist = results[0]
            artist_details = {
                'discogs_id': artist.id,
                'profile': format_string(artist.profile),  # Format the profile string
                'aliases': [alias.name for alias in artist.aliases],  # Save as list
                'members': [format_string(member.name) for member in artist.members],  # Save as list and format
                'urls': [str(url) for url in artist.urls],  # Save as list
            }

            # # Save the artist details to the database
            # with transaction.atomic():  # Use atomic transaction for data consistency
            #     artist_instance, created = Artist.objects.get_or_create(id=artist_id, defaults={
            #         'name': artist_name,
            #         'photo_url': '',
            #         'popularity': 0,
            #     })
            #     artist_instance.discogs_id = artist_details['discogs_id']
            #     artist_instance.profile = artist_details['profile']
            #     artist_instance.aliases = artist_details['aliases']
            #     artist_instance.members = artist_details['members']
            #     artist_instance.urls = artist_details['urls']
            #     artist_instance.save()

            # Cache the result for 1 hour
            cache.set(cache_key, artist_details, timeout=3600)  # Cache for 1 hour

            return artist_details

    except Exception as e:
        print(f"Error fetching data from Discogs: {e}")
    return {}

def update_artist_from_discogs_url(artist, discogs_url):
    """
    Update the artist in the database based on the Discogs URL provided.
    
    Args:
        artist (Artist): The artist object to update.
        discogs_url (str): The Discogs URL provided by the user.
    """
    match = re.search(r'/artist/(\d+)-', discogs_url)
    if (match):
        discogs_id = match.group(1)
        try:
            discogs_artist = d.artist(discogs_id)
            artist.discogs_id = discogs_id
            artist.profile = format_string(discogs_artist.profile)  # Format the profile string
            artist.aliases = [alias.name for alias in discogs_artist.aliases]  # Save as list
            artist.members = [format_string(member.name) for member in discogs_artist.members]  # Save as list and format
            artist.urls = [str(url) for url in discogs_artist.urls]  # Ensure URLs are strings
            artist.save()
        except Exception as e:
            print(f"Error updating artist from Discogs: {e}")

def get_more_album_data(spotify_id, album_name, artist_name, user):
    """
    Fetch additional album data from Discogs API.
    
    Args:
        album_name (str): The name of the album.
        user (User): The user requesting the data.
    
    Returns:
        dict: A dictionary containing additional album data.
    """
    # cache_key = f"album_data_{album_name.lower().strip()}"
    # cached_data = cache.get(cache_key)
    
    # if cached_data:
    #     return cached_data

    try:
        print(f"Fetching album data for {album_name}")
        results = d.search(album_name, type='release', per_page=15, page=1, artist=artist_name)
        if results:
            album = results[0]
            print(f"Album found: {album.title}")
            album_details = {
                'discogs_id': album.id,
                'genres': album.genres,
                'styles': album.styles,
                'tracklist': [{'position': track.position, 'title': track.title, 'duration': track.duration} for track in album.tracklist],
                'labels': [label.name for label in album.labels],
                # 'formats': [format.name for format in album.formats],
                # 'lowest_price': album.lowest_price,
                # 'current_price': album.current_price,
                # 'highest_price': album.highest_price,
            }
            print(f"Album details: {album_details}")

            # # Cache the result for 1 hour
            # cache.set(cache_key, album_details, timeout=3600)  # Cache for 1 hour

            return album_details

    except Exception as e:
        print(f"Error fetching data from Discogs: {e}")
    return {}
