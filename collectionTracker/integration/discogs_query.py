from decouple import config
import discogs_client
from django.core.cache import cache
from collection.models import Album
from stats.models import DailyAlbumPrice
import re
from integration.exchangeRate_query import usd_to_eur
from datetime import date


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
    Format the string by removing the formatting logic specifig to Discogs.

    Args:
        string (str): The original string.

    Returns:
        str: The formatted string.
    """
    # Remove round brackets with only numbers inside
    formatted_string = re.sub(r'\(\d+\)', '', string)
    
    # Replace [b] and [/b] 
    formatted_string = re.sub(r'\[b\]', '', formatted_string)
    formatted_string = re.sub(r'\[/b\]', '', formatted_string)
    formatted_string = re.sub(r'\[i\]', '', formatted_string)
    formatted_string = re.sub(r'\[/i\]', '', formatted_string)

    # Remove the [l= and [a= parts and the surrounding brackets
    formatted_string = re.sub(r'\[a=|\[l=', '', formatted_string)

    # Remove sentences containing remaining [] brackets
    formatted_string = re.sub(r'[^.]*\[.*?\][^.]*\.', '', formatted_string)
    formatted_string = re.sub(r'[^.]*\[.*?\]', '', formatted_string)

    return formatted_string

def get_more_artist_data(artist_name):
    """
    Fetch additional artist data from Discogs API.
    
    Args:
        artist_id (str): The Spotify ID of the artist.
        artist_name (str): The name of the artist.
        user (User): The user requesting the data.
    
    Returns:
        dict: A dictionary containing additional artist data.
    """
    cache_key = f"artist_data_with_releases_{artist_name.lower().replace(' ', '_')}"
    cached_data = cache.get(cache_key)
    
    if (cached_data):
        return cached_data

    try:
        results = d.search(artist_name, type='artist', per_page=15, page=1, exact=True)
        if (results):
            artist = results[0]
            artist_details = {
                'discogs_id': getattr(artist, 'id', ''),
                'profile': format_string(getattr(artist, 'profile', 'N/A')),  # Format the profile string
                'aliases': [format_string(alias.name) for alias in getattr(artist, 'aliases', [])],  # Save as list
                'members': [format_string(member.name) for member in getattr(artist, 'members', [])],  # Save as list and format
                'urls': [str(url) for url in getattr(artist, 'urls', [])],  # Save as list
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
            artist.profile = format_string(discogs_artist.profile)  # Format the profile string
            artist.aliases = [format_string(alias.name) for alias in discogs_artist.aliases]  # Save as list
            artist.members = [format_string(member.name) for member in discogs_artist.members]  # Save as list and format
            artist.urls = [str(url) for url in discogs_artist.urls]  # Ensure URLs are strings
            artist.save()
        except Exception as e:
            print(f"Error updating artist from Discogs: {e}")

def update_album_from_discogs_url(album, discogs_url):
    """
    Update the album in the database based on the Discogs URL provided.
    
    Args:
        album (Album): The album object to update.
        discogs_url (str): The Discogs URL provided by the user.
    """
    match = re.search(r'/release/(\d+)-', discogs_url)
    if match:
        discogs_id = match.group(1)
        try:
            release = d.release(discogs_id)
            album.discogs_id = discogs_id
            album.title = format_string(release.title)
            album.year = release.year
            album.genres = [format_string(genre) for genre in release.genres]
            album.styles = [format_string(style) for style in release.styles]
            album.tracklist = [{'position': track.position, 'title': track.title, 'duration': track.duration} for track in release.tracklist]
            album.labels = [format_string(label.name) for label in release.labels]
            lowest_price_usd = release.fetch('lowest_price')
            if lowest_price_usd is not None:
                album.lowest_price = round(float(usd_to_eur(lowest_price_usd)), 2)
            album.save()
        except Exception as e:
            print(f"Error updating album from Discogs: {e}")

def fetch_basic_album_details(album_id):
    """
    Fetch basic album details from Discogs API.
    
    Args:
        album_id(str): Spotify album ID.
    
    Returns:
        dict: A dictionary containing basic album details.
    """
    album = Album.objects.get(id=album_id)
    try:
        results = d.search(album.name, type='release', per_page=15, page=1, artist=album.artist.name)
        if results:
            album = results[0]
            release = d.release(album.id)
            lowest_price_usd = release.fetch('lowest_price')
            lowest_price_eur = round(float(usd_to_eur(lowest_price_usd)), 2) if lowest_price_usd is not None else None

            album_details = {
                'discogs_id': album.id,
                'genres': album.genres,
                'styles': album.styles,
                'labels': [format_string(label.name) for label in album.labels],
                'tracklist': [{'position': track.position, 'title': track.title, 'duration': track.duration} for track in album.tracklist],
                'lowest_price': lowest_price_eur,
            }        
            return album_details
    except Exception as e:
        print(f"Error fetching basic album details from Discogs: {e}")
    return {}

def fetch_album_price(album_id):
    """
    Fetch basic album details from Discogs API.
    
    Args:
        album_id(str): Spotify album ID.
    
    Returns:
        dict: A dictionary containing basic album details.
    """
    album = Album.objects.get(id=album_id)
    print("---------------------------------")
    print(f"Album Name: {album.name}")
    try:
        results = d.search(album.name, type='release', per_page=15, page=1, artist=album.artist.name)
        if results:
            album_result = results[0]
            print(f"Album Result: {album_result}")
            release = d.release(album_result.id)
            lowest_price_usd = release.fetch('lowest_price')
            lowest_price_eur = round(float(usd_to_eur(lowest_price_usd)), 2) if lowest_price_usd is not None else None
            print(f"Lowest Price: {lowest_price_eur}")
            discogs_id = release.id
            print(f"Discogs ID: {discogs_id}")

            album_details = {
                'discogs_id': discogs_id,
                'lowest_price': lowest_price_eur,
            }
            return album_details
    except Exception as e:
        print(f"Error fetching basic album details from Discogs: {e}")
    return {}

def update_album_price(album_id):
    """
    Update album price in the database with data fetched from Discogs API.
    
    Args:
        album_id(str): Spotify album ID.
    
    Returns:
        bool: True if update was successful, False otherwise.
    """
    album_details = fetch_album_price(album_id)
    if not album_details:
        return False

    try:
        album = Album.objects.get(id=album_id)
        if album.discogs_id is None:
            album.discogs_id = album_details['discogs_id']
        album.lowest_price = album_details['lowest_price']
        album.save()

        # Create a new entry for DailyAlbumPrice
        daily_price = DailyAlbumPrice(
            album=album,
            date=date.today(),
            price=album_details['lowest_price']
        )
        daily_price.save()

        return True
    except Exception as e:
        print(f"Error updating album details: {e}")
        return False