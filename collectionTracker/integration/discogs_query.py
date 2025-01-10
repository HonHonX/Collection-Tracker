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

def get_more_artist_data(artist_id, artist_name):
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
            artist.profile = format_string(discogs_artist.profile) if discogs_artist.profile else ''  # Format the profile string
            artist.aliases = [alias.name for alias in discogs_artist.aliases] if discogs_artist.aliases else []  # Save as list
            artist.members = [format_string(member.name) for member in discogs_artist.members] if discogs_artist.members else []  # Save as list and format
            artist.urls = [str(url) for url in discogs_artist.urls] if discogs_artist.urls else []  # Ensure URLs are strings
            artist.save()
        except Exception as e:
            print(f"Error updating artist from Discogs: {e}")

def fetch_basic_album_details(album_name, artist_name):
    """
    Fetch basic album details from Discogs API.
    
    Args:
        album_name (str): The name of the album.
        artist_name (str): The name of the artist.
    
    Returns:
        dict: A dictionary containing basic album details.
    """
    try:
        print(f"Fetching basic album details for {album_name}")
        results = d.search(album_name, type='release', per_page=15, page=1, artist=artist_name)
        if results:
            album = results[0]
            print(f"Album found: {album.title}")
            album_details = {
                'discogs_id': album.id,
                'genres': album.genres if hasattr(album, 'genres') else [],
                'styles': album.styles if hasattr(album, 'styles') else [],
                'labels': [label.name for label in album.labels] if hasattr(album, 'labels') else [],
            }
            
            return album_details
    except Exception as e:
        print(f"Error fetching basic album details from Discogs: {e}")
    return {}


def fetch_album_tracklist_and_formats(discogs_id):
    """
    Fetch tracklist and formats for an album from Discogs API.
    
    Args:
        discogs_id (int): The Discogs ID of the album.
    
    Returns:
        dict: A dictionary containing the tracklist and formats of the album.
    """
    try:
        print(f"Fetching tracklist and formats for Discogs ID: {discogs_id}")
        album = d.release(discogs_id)
        tracklist_and_formats = {
            'tracklist': [{'position': track.position, 'title': track.title, 'duration': track.duration} for track in album.tracklist],
            #'formats': [{'name': f['name'], 'qty': f['qty'], 'descriptions': f.get('descriptions', [])} for f in album.formats]
        }
        return tracklist_and_formats
    except Exception as e:
        print(f"Error fetching tracklist and formats from Discogs: {e}")
    return {}

def save_basic_album_details(artist_id):
    album_results = Album.objects.filter(artist_id=artist_id)
    print(album_results)
    for album_instance in album_results:
        more_album_data = fetch_basic_album_details(album_instance.name, album_instance.artist.name)
        print(f"More album data: {more_album_data}")
        album_instance.discogs_id = more_album_data.get('discogs_id')
        album_instance.genres = more_album_data.get('genres', [])
        album_instance.styles = more_album_data.get('styles', [])
        album_instance.labels = more_album_data.get('labels', [])
        # album_instance.lowest_price = more_album_data.get('lowest_price', 0)
        album_instance.save()
    # Refresh the artist object to get the updated data
    album_instance.refresh_from_db()


def save_additional_album_details(album_id):
    try:
        album_results = Album.objects.filter(album_id=album_id)
        if not album_results:
            raise ValueError(f"No album found with id {album_id}")
        
        album_instance = album_results[0]
        discogs_id = album_instance.discogs_id

        if discogs_id:
            more_album_data = fetch_album_tracklist_and_formats(discogs_id)
            album_instance.tracklist = more_album_data.get('tracklist', [])
            #album_instance.formats = more_album_data.get('formats', [])
            album_instance.save()
            # Refresh the artist object to get the updated data
            album_instance.refresh_from_db()

    except Exception as e:
        print(f"An error occurred while saving additional album details: {e}")