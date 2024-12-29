from django.shortcuts import render, get_object_or_404
from django.views import View
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Album, Artist, UserAlbumCollection, UserAlbumDescription, UserAlbumWishlist

@login_required
def album_overview(request):
    # Get the user's album collection
    user_collection = UserAlbumCollection.objects.filter(user=request.user)
    
    # Extract album IDs for the user's collection
    user_album_ids = list(user_collection.values_list('album__id', flat=True))
    
    # Get the user's album wishlist
    user_wishlist = UserAlbumWishlist.objects.filter(user=request.user)
    
    # Extract album IDs for the user's wishlist
    user_wishlist_ids = list(user_wishlist.values_list('album__id', flat=True))
    print(user_wishlist_ids)
    
    # Get the list of artists from the user's collection (unique artists)
    artist_list = Artist.objects.filter(album__useralbumcollection__user=request.user).distinct()

    # If there's an artist filter in the request, apply it
    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        user_collection = user_collection.filter(album__artist__name=artist_filter)

    return render(request, 'collection/album_overview.html', {
        'user_collection': user_collection,
        'user_album_ids': user_album_ids,
        'user_wishlist_ids': user_wishlist_ids,  
        'artist_list': artist_list,
    })

@csrf_exempt
@login_required
def add_album_to_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        artist_name = data.get('artist_name')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})

        # Artist erstellen oder laden
        artist, _ = Artist.objects.get_or_create(name=artist_name)

        # Album erstellen oder laden
        album, _ = Album.objects.get_or_create(
            id=album_id,
            defaults={
                'name': data.get('album_name'),
                'album_type': data.get('album_type'),
                'release_date': data.get('release_date'),
                'image_url': data.get('image_url'),
                'artist': artist,
            }
        )

        try:
            UserAlbumCollection.objects.get(user=user, album=album)
            return JsonResponse({'success': False, 'message': f'Album "{album.name}" is already in your collection.'})
        except UserAlbumCollection.DoesNotExist:
            UserAlbumCollection.objects.create(user=user, album=album)
            return JsonResponse({'success': True, 'message': f'Album "{album.name}" added to your collection!'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# API endpoint to remove an album from the user's collection (AJAX request)
@csrf_exempt
@login_required
def remove_album_from_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse JSON request body
        album_id = data.get('album_id')
        
        try:
            # Find and delete the entry in the user's collection
            collection_entry = UserAlbumCollection.objects.get(user=request.user, album__id=album_id)
            collection_entry.delete()
            return JsonResponse({'success': True, 'message': f'Album with ID "{album_id}" removed from your collection.'})
        
        except UserAlbumCollection.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found in your collection.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def save_description(request, album_id):
    if request.method == "POST" and request.user.is_authenticated:
        description = request.POST.get('description')

        try:
            album = Album.objects.get(id=album_id)

            # Get or create the UserAlbumDescription for the current user and album
            user_description, created = UserAlbumDescription.objects.get_or_create(
                user=request.user,
                album=album,
            )

            # Update the description
            user_description.description = description
            user_description.save()

            # Return a JSON response indicating success
            return JsonResponse({'success': True})

        except Album.DoesNotExist:
            # Handle the case where the album doesn't exist
            return JsonResponse({'success': False, 'error': 'Album not found'})
        except Exception as e:
            # Handle other errors
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method or user not authenticated'})

class AlbumDetail(View):
    """Displays the details of an album."""

    def get(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)

        # Check if the user is authenticated and if the album is in their collection
        in_collection = False
        in_wishlist = False
        if request.user.is_authenticated:
            in_collection = UserAlbumCollection.objects.filter(user=request.user, album=album).exists()
            in_wishlist = UserAlbumWishlist.objects.filter(user=request.user, album=album).exists()

            # Get the user's description for the album, if it exists
            user_description = UserAlbumDescription.objects.filter(user=request.user, album=album).first()
        else:
            user_description = None

        context = {
            'album': album,
            'artist': album.artist,
            'in_collection': in_collection,  # Pass the collection status
            'in_wishlist': in_wishlist,  # Pass the collection status
            'user_description': user_description,  # Pass user's description (if any)
        }

        return render(request, 'collection/album_detail.html', context)

    def post(self, request, album_id):
        """Handles updating the album description for the current user."""
        album = get_object_or_404(Album, id=album_id)

        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=403)  # Forbidden for unauthenticated users

        user_description, created = UserAlbumDescription.objects.get_or_create(
            user=request.user,
            album=album
        )

        description = request.POST.get('description', '').strip()  # Ensure stripping whitespace
        if description:
            user_description.description = description
            user_description.save()
            # Return a JSON response indicating success with status 200
            return JsonResponse({'success': True, 'message': 'Description updated successfully'}, status=200)

        # If no description is provided, return an error with status 400
        return JsonResponse({'success': False, 'error': 'Description cannot be empty'}, status=400)
    
# Add album to wishlist
@csrf_exempt
@login_required
def add_album_to_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        artist_name = data.get('artist_name')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})

        # Artist erstellen oder laden
        artist, _ = Artist.objects.get_or_create(name=artist_name)

        # Album erstellen oder laden
        album, _ = Album.objects.get_or_create(
            id=album_id,
            defaults={
                'name': data.get('album_name'),
                'album_type': data.get('album_type'),
                'release_date': data.get('release_date'),
                'image_url': data.get('image_url'),
                'artist': artist,
            }
        )

        try:
            UserAlbumWishlist.objects.get(user=user, album=album)
            return JsonResponse({'success': False, 'message': f'Album "{album.name}" is already in your wishlist.'})
        except UserAlbumWishlist.DoesNotExist:
            UserAlbumWishlist.objects.create(user=user, album=album)
            return JsonResponse({'success': True, 'message': f'Album "{album.name}" added to your wishlist!'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# Remove album from wishlist
@csrf_exempt
@login_required
def remove_album_from_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse JSON request body
        album_id = data.get('album_id')
        
        try:
            # Find and delete the entry in the user's wishlist
            wishlist_entry = UserAlbumWishlist.objects.get(user=request.user, album__id=album_id)
            wishlist_entry.delete()
            return JsonResponse({'success': True, 'message': f'Album with ID "{album_id}" removed from your wishlist.'})
        
        except UserAlbumWishlist.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found in your wishlist.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# views.py
@login_required
def wishlist_overview(request):
    # Get the user's album collection
    user_collection = UserAlbumCollection.objects.filter(user=request.user)
    
    # Extract album IDs for the user's collection
    user_album_ids = list(user_collection.values_list('album__id', flat=True))
    
    # Get the user's album wishlist
    user_wishlist = UserAlbumWishlist.objects.filter(user=request.user)
    
    # Extract album IDs for the user's wishlist
    user_wishlist_ids = list(user_wishlist.values_list('album__id', flat=True))
    
    # Get the list of artists from the user's collection (unique artists)
    artist_list = Artist.objects.filter(album__useralbumcollection__user=request.user).distinct()

    # If there's an artist filter in the request, apply it
    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        user_wishlist = user_wishlist.filter(album__artist__name=artist_filter)

    return render(request, 'collection/wishlist_overview.html', {
        'user_wishlist': user_wishlist,
        'user_wishlist_ids': user_wishlist_ids,
        'user_album_ids': user_album_ids,
        'artist_list': artist_list,
    })

    