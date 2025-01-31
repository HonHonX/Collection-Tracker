import json
import logging
import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Album, Artist, RecommendedArtist, UserAlbumBlacklist, UserAlbumCollection, UserAlbumDescription, UserAlbumWishlist, UserFollowedArtists
from .tasks import start_background_album_update, start_background_artist_update
from integration.discogs_query import fetch_basic_album_details, update_album_from_discogs_url, update_artist_from_discogs_url
from integration.lastfm_query import artist_recommendations
from integration.spotify_query import get_artist_data
from stats.models import AlbumPricePrediction, DailyAlbumPrice
from utils.collection_helpers import filter_list_by_artist, get_artist_list, get_followed_artists, get_newest_albums, get_user_album_ids, get_user_lists
from utils.stats_helpers import calculate_top_genres

logger = logging.getLogger(__name__)

@login_required
def home_view(request):
    """
    Home view that displays the user's followed artists and their albums.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered home page. 
    """
    followed_artists = []
    recommended_artists = []
    if request.user.is_authenticated:
        followed_artists = get_followed_artists(request.user)
        # Fetch recommended artists
        response = get_recommendations(request)
        if response.status_code == 200:
            recommended_artists = json.loads(response.content).get('recommended_artists', [])
    user_album_ids, user_blacklist_ids, user_wishlist_ids = get_user_lists(request.user)
    newest_albums = get_newest_albums(request.user)

    return render(request, 'collection/index.html', {  
        'settings': settings,
        'followed_artists': followed_artists,
        'recommended_artists': recommended_artists,
        'user_album_ids': user_album_ids,  
        'user_blacklist_ids': user_blacklist_ids,
        'user_wishlist_ids': user_wishlist_ids,
        'newest_albums': newest_albums,
    })

def artist_detail(request, artist_id):
    """
    Render the artist detail page with the specified artist ID.
    
    Args:
        request (HttpRequest): The HTTP request object.
        artist_id (int): The ID of the artist to display.
    
    Returns:
        HttpResponse: The rendered HTML page with artist details.
    """
    artist = get_object_or_404(Artist, id=artist_id)
    
    if request.method == 'POST':
        discogs_url = request.POST.get('discogs_url')
        if (discogs_url):
            update_artist_from_discogs_url(artist, discogs_url) 
            return redirect('artist_detail', artist_id=artist.id)
    
    return render(request, 'collection/artist_detail.html', {'artist': artist}) 

def artist_search(request, artist_name=None):
    """
    Handle artist search requests.
    
    If the request method is POST, retrieve the artist name from the request and fetch artist data.
    If the artist name is not provided, render the search page with an error message.
    If an exception occurs during data retrieval, return a JSON response with the error message.
    If the request method is not POST, render the search page.
    
    Args:
        request (HttpRequest): The HTTP request object.
        artist_name (str): The name of the artist to search for.
    
    Returns:
        HttpResponse: The rendered HTML page or JSON response with error message.
    """

    user = request.user

    if request.method == 'POST' or artist_name:
        if not artist_name:
            artist_name = request.POST.get('artist_name')
        
        if not artist_name:
            error = "Artist name is required."
            return render(request, 'collection/artist_search.html', {
                'artist_name': '',
                'error': error,
            })
        
        try:
            context = get_artist_data(artist_name, user)
            response = render(request, 'collection/artist_overview.html', context)
            
            start_background_artist_update(context['artist'].id)
            logger.info(f"Started background task for artist ID: {context['artist'].id}")
            
            return response
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return render(request, 'collection/artist_search.html')

def artist_overview(request, artist_id):
    """ 
    Render the artist overview page. 
    Fetch and display detailed information about the specified artist.
    
    Args:
        request (HttpRequest): The HTTP request object.
        artist_id (str): The id of the artist to display.
    
    Returns:
        HttpResponse: The rendered HTML page with artist details.
    """
    try:
        artist = Artist.objects.get(id=artist_id)
        artist_name = artist.name

        return redirect('artist_search', artist_name=artist_name)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@csrf_exempt
@login_required
def follow_artist(request):
    """
    Handle follow/unfollow artist requests.
    
    If the request method is POST, retrieve the artist data from the request and update the user's followed artists.
    If the artist is already followed, unfollow the artist. Otherwise, follow the artist.
    The code for "follow_artist" has been created with the help of AI.
    
    Args:
        request (HttpRequest): The HTTP request object.
    
    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            artist_id = data.get('artist_id')

            artist = Artist.objects.get(id=artist_id)

            follow_entry, created = UserFollowedArtists.objects.get_or_create(user=user, artist=artist)

            if not created:
                follow_entry.delete()
                return JsonResponse({'success': True, 'message': 'Artist unfollowed.'})
            else:
                return JsonResponse({'success': True, 'message': 'Artist followed.'})
        except Artist.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Artist does not exist.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def list_overview(request, list_type):
    """
    Render the list overview page based on the list type (collection, wishlist, or blacklist).
    
    Args:
        request (HttpRequest): The HTTP request object.
        list_type (str): The type of the list to display (collection, wishlist, or blacklist).
    
    Returns:
        HttpResponse: The rendered HTML page with the list details.
    """
    try:
        user_album_ids, user_wishlist_ids, user_blacklist_ids, user_collection, user_wishlist, user_blacklist = get_user_album_ids(request.user)
        recommended_album = None
        avg_predicted_price = None
        current_price = None

        if list_type == 'collection':
            user_list = filter_list_by_artist(request, user_collection)
            template = 'collection/album_overview.html'
        elif list_type == 'wishlist':
            user_list = filter_list_by_artist(request, user_wishlist)
            template = 'collection/wishlist_overview.html'
            if user_wishlist.exists():
                best_price_change = None

                for wishlist_entry in user_wishlist:
                    album = wishlist_entry.album
                    daily_prices = DailyAlbumPrice.objects.filter(album=album).order_by('-date')[:7]

                    if daily_prices.exists():
                        predicted_prices = AlbumPricePrediction.objects.filter(album=album).order_by('-date')[:7]
                        if predicted_prices.exists():
                            avg_predicted_price = round(sum([price.predicted_price for price in predicted_prices]) / len(predicted_prices), 2)
                            current_price = daily_prices.first().price
                            price_change = avg_predicted_price - current_price

                            if best_price_change is None or price_change > best_price_change:
                                best_price_change = price_change
                                recommended_album = album
        elif list_type == 'blacklist':
            user_list = filter_list_by_artist(request, user_blacklist)
            template = 'collection/blacklist_overview.html'
        else:
            return JsonResponse({'success': False, 'error': 'Invalid list type'}, status=400)

        artist_list = get_artist_list(request.user)  # Retrieve artist list
        user_album_substatuses = UserAlbumCollection.SUBSTATUS
        user_album_priorities = UserAlbumWishlist.PRIORITY_CHOICES
        user_albums = Album.objects.filter(useralbumcollection__user=request.user)  

        return render(request, template, {
            'user': request.user,
            'user_blacklist': user_blacklist,
            'user_blacklist_ids': user_blacklist_ids,
            'user_wishlist': user_wishlist,
            'user_wishlist_ids': user_wishlist_ids,
            'user_collection': user_collection,
            'user_album_ids': user_album_ids,
            'artist_list': artist_list,
            'user_list': user_list,
            'albums': user_albums,
            'user_album_substatuses': [choice[1] for choice in user_album_substatuses],
            'user_album_priorities': [choice[1] for choice in user_album_priorities],
            'recommended_album': recommended_album,
            'avg_predicted_price': avg_predicted_price,
            'current_price': current_price,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
# Generic album management view
@login_required
def manage_album(request, list_type, action):
    """
    Handle adding or removing albums from the user's collection, wishlist, or blacklist.
    
    Args:
        request (HttpRequest): The HTTP request object.
        list_type (str): The type of the list (collection, wishlist, or blacklist).
        action (str): The action to perform (add or remove).
    
    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            album_id = data.get('album_id')
            album_name = data.get('album_name')
            album_type = data.get('album_type')
            release_date = data.get('release_date')
            image_url = data.get('image_url')

            user = request.user

            album, _ = Album.objects.get_or_create(
                id=album_id,
                defaults={
                    'name': album_name,
                    'album_type': album_type,
                    'release_date': release_date,
                    'image_url': image_url,
                }
            )

            if list_type == 'collection':
                if action == 'add':
                    UserAlbumCollection.objects.get_or_create(user=user, album=album)
                elif action == 'remove':
                    UserAlbumCollection.objects.filter(user=user, album=album).delete()
            elif list_type == 'wishlist':
                if action == 'add':
                    UserAlbumWishlist.objects.get_or_create(user=user, album=album)
                elif action == 'remove':
                    UserAlbumWishlist.objects.filter(user=user, album=album).delete()
            elif list_type == 'blacklist':
                if action == 'add':
                    UserAlbumBlacklist.objects.get_or_create(user=user, album=album)
                elif action == 'remove':
                    UserAlbumBlacklist.objects.filter(user=user, album=album).delete()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

class AlbumDetail(View):
    """
    View class to handle displaying and updating album details.
    """
    def get(self, request, album_id):
        """
        Handle GET requests to display album details.
        
        Args:
            request (HttpRequest): The HTTP request object.
            album_id (int): The ID of the album to display.
        
        Returns:
            HttpResponse: The rendered HTML page with album details or JSON response with error message.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        try:
            album = get_object_or_404(Album, id=album_id)
            if album:
                logger.info(f"Album {album.name} with the id {album.id} found in database.")
                album_data = fetch_basic_album_details(album.id)
                
                if not album.discogs_id:
                    album.discogs_id = album_data.get('discogs_id')
                    album.genres = album_data.get('genres')
                    album.styles = album_data.get('styles')
                    album.labels = album_data.get('labels')
                    album.tracklist = album_data.get('tracklist')
                    album.lowest_price = album_data.get('lowest_price')
                    album.save()

                if album.lowest_price:
                    DailyAlbumPrice.objects.get_or_create(
                        album=album,
                        date=timezone.now().date(),
                        defaults={'price': album.lowest_price}
                    )

            collection_entry = UserAlbumCollection.objects.filter(user=request.user, album=album).first()
            wishlist_entry = UserAlbumWishlist.objects.filter(user=request.user, album=album).first()
            user_description = UserAlbumDescription.objects.filter(user=request.user, album=album).first()

            context = {
                'album': album,
                'collection_entry': collection_entry,
                'wishlist_entry': wishlist_entry,
                'in_collection': bool(collection_entry),
                'in_wishlist': bool(wishlist_entry),
                'user_description': user_description,
                'priority_display': wishlist_entry.get_priority_display() if wishlist_entry else None,
                'substatus_display': collection_entry.get_substatus_display() if collection_entry else None,
            }
 
            return render(request, 'collection/album_detail.html', context)
        except Exception as e:
            logger.error(f"Error fetching album details: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def post(self, request, album_id):
        """
        Handle POST requests to update album details.
        
        Args:
            request (HttpRequest): The HTTP request object.
            album_id (int): The ID of the album to update.
        
        Returns:
            JsonResponse: A JSON response indicating success or failure.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        try:
            album = get_object_or_404(Album, id=album_id)

            if 'description' in request.POST:
                return self.update_description(request, album)

            if 'priority' in request.POST:
                return self.update_priority(request, album)

            if 'substatus' in request.POST:
                return self.update_substatus(request, album)

            if 'discogs_url' in request.POST:
                discogs_url = request.POST.get('discogs_url')
                if discogs_url:
                    update_album_from_discogs_url(album, discogs_url)
                    start_background_album_update(album.id)  # Start background update for album details
                    return redirect('album_detail', album_id=album.id)

            return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def update_description(self, request, album):
        """
        Update the description of the album.
        
        Args:
            request (HttpRequest): The HTTP request object.
            album (Album): The album object to update.
        
        Returns:
            JsonResponse: A JSON response indicating success or failure.
        """
        description = request.POST.get('description', '').strip()  # Strip whitespace
        user_description, created = UserAlbumDescription.objects.get_or_create(user=request.user, album=album)
        user_description.description = description or None
        user_description.save()
        return JsonResponse({'success': True, 'message': 'Description updated successfully'}, status=200)

    def update_priority(self, request, album):
        """
        Update the priority of the album in the user's wishlist.
        
        Args:
            request (HttpRequest): The HTTP request object.
            album (Album): The album object to update.
        
        Returns:
            JsonResponse: A JSON response indicating success or failure.
        """
        priority = request.POST.get('priority', '').strip()

        try:
            priority = int(priority)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Priority must be a valid integer'}, status=400)

        valid_priorities = [choice[0] for choice in UserAlbumWishlist.PRIORITY_CHOICES]
        if priority not in valid_priorities:
            return JsonResponse({'success': False, 'error': f'Invalid priority value: {priority}'}, status=400)

        wishlist_entry = UserAlbumWishlist.objects.filter(user=request.user, album=album).first()
        if not wishlist_entry:
            return JsonResponse({'success': False, 'error': 'Album is not in your wishlist'}, status=400)

        wishlist_entry.priority = priority
        wishlist_entry.save()

        return JsonResponse({
            'success': True,
            'message': 'Priority updated successfully',
            'priority_display': wishlist_entry.get_priority_display()
        }, status=200)

    def update_substatus(self, request, album):
        """
        Update the substatus(like delivered, preordered etc.) of the album in the user's collection.
        
        Args:
            request (HttpRequest): The HTTP request object.
            album (Album): The album object to update.
        
        Returns:
            JsonResponse: A JSON response indicating success or failure.
        """
        substatus = request.POST.get('substatus', '')
        collection_entry = UserAlbumCollection.objects.filter(user=request.user, album=album).first()
        
        valid_substatuses = [choice[0] for choice in UserAlbumCollection.SUBSTATUS]
        if substatus not in valid_substatuses:
            return JsonResponse({'success': False, 'error': 'Invalid substatus value'}, status=400)

        if not collection_entry:
            return JsonResponse({'success': False, 'error': 'Album is not in your collection'}, status=400)

        collection_entry.substatus = substatus
        collection_entry.save()

        return JsonResponse({
            'success': True,
            'message': 'Substatus updated successfully',
            'substatus_display': collection_entry.get_substatus_display()
        }, status=200)

@login_required
def album_carousel(request):
    """
    Render the album carousel page.
    
    Args:
        request (HttpRequest): The HTTP request object.
    
    Returns:
        HttpResponse: The rendered HTML page with the user's albums.
    """
    user_albums = Album.objects.filter(useralbumcollection__user=request.user)
    return render(request, 'collection/album_carousel.html', {'albums': user_albums})

@login_required
def get_recommendations(request):
    """
    Fetch and return recommended artists for the user.
    
    Args:
        request (HttpRequest): The HTTP request object.
    
    Returns:
        JsonResponse: A JSON response containing recommended artists.
    """
    user = request.user 
    recommended_artists = RecommendedArtist.objects.filter(user=user)

    if not recommended_artists.exists():
        recommended_artists = fetch_and_save_recommendations(user)

    return JsonResponse({
        'recommended_artists': [
            {
                'id': rec.artist.id,
                'name': rec.artist.name,
                'image_url': rec.artist.photo_url or '/static/img/default.jpg'
            }
            for rec in recommended_artists
        ]
    })

def fetch_and_save_recommendations(user):
    """
    Fetch and save artist recommendations for the user.
    
    Args:
        user (User): The user object.
    
    Returns:
        QuerySet: A queryset of recommended artists.
    """
    top_genres = calculate_top_genres(user)
    genres = [genre.name for genre in top_genres]
    
    try:
        response = artist_recommendations(genres) 
        data = response.json() if isinstance(response, requests.Response) else json.loads(response.content)
        artists = data.get('artists', [])
        error = None

        artist_objects = []
        for name in artists:
            artist_data = get_artist_data(name, user)
            artist_objects.append(artist_data['artist'])

        followed_artist_ids = UserFollowedArtists.objects.filter(user=user).values_list('artist_id', flat=True)
        recommended_artists = [
            artist for artist in artist_objects if artist.id not in followed_artist_ids
        ]

        RecommendedArtist.objects.filter(user=user).delete()
        for artist in recommended_artists:
            RecommendedArtist.objects.create(user=user, artist=artist)

        return RecommendedArtist.objects.filter(user=user)

    except requests.exceptions.RequestException as e:
        return []

@login_required
def reload_recommendations(request):
    """
    Reload and return updated artist recommendations for the user.
    
    Args:
        request (HttpRequest): The HTTP request object.
    
    Returns:
        JsonResponse: A JSON response containing updated recommended artists.
    """
    user = request.user
    recommended_artists = fetch_and_save_recommendations(user)
    return JsonResponse({
        'recommended_artists': [
            {
                'id': rec.artist.id,
                'name': rec.artist.name,
                'image_url': rec.artist.photo_url or '/static/img/default.jpg'
            }
            for rec in recommended_artists
        ]
    })
