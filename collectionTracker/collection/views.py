from django.shortcuts import render, get_object_or_404
from django.views import View
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Album, Artist, UserAlbumCollection, UserAlbumDescription
import logging

# Set up a logger
logger = logging.getLogger(__name__)

def save_description(request, album_id):
    logger.debug(f"save_description called with album_id={album_id}")

    if request.method == "POST" and request.user.is_authenticated:
        description = request.POST.get('description')
        logger.debug(f"Received description: {description}")

        try:
            album = Album.objects.get(id=album_id)
            logger.debug(f"Found album with id={album_id}")

            # Get or create the UserAlbumDescription for the current user and album
            user_description, created = UserAlbumDescription.objects.get_or_create(
                user=request.user,
                album=album,
            )
            logger.debug(f"UserAlbumDescription {'created' if created else 'retrieved'} for user={request.user.id}, album={album.id}")

            # Update the description
            user_description.description = description
            user_description.save()
            logger.debug(f"Description for album {album_id} updated successfully.")

            # Return a JSON response indicating success
            return JsonResponse({'success': True})

        except Album.DoesNotExist:
            logger.error(f"Album with id={album_id} does not exist.")
            # Handle the case where the album doesn't exist
            return JsonResponse({'success': False, 'error': 'Album not found'})
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {str(e)}")
            # Handle other errors
            return JsonResponse({'success': False, 'error': str(e)})

    logger.warning("Invalid request method or user not authenticated.")
    return JsonResponse({'success': False, 'error': 'Invalid request method or user not authenticated'})

class AlbumDetail(View):
    """Displays the details of an album."""

    def get(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)

        # Check if the user is authenticated and if the album is in their collection
        in_collection = False
        if request.user.is_authenticated:
            in_collection = UserAlbumCollection.objects.filter(user=request.user, album=album).exists()

            # Get the user's description for the album, if it exists
            user_description = UserAlbumDescription.objects.filter(user=request.user, album=album).first()
        else:
            user_description = None

        context = {
            'album': album,
            'artist': album.artist,
            'in_collection': in_collection,  # Pass the collection status
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

@csrf_exempt
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


@login_required
def album_overview(request):
    # Get the user's album collection
    user_collection = UserAlbumCollection.objects.filter(user=request.user)
    
    # Extract album IDs for the user's collection
    user_album_ids = list(user_collection.values_list('album__id', flat=True))
    
    # Get the list of artists from the user's collection (unique artists)
    artist_list = Artist.objects.filter(album__useralbumcollection__user=request.user).distinct()

    # If there's an artist filter in the request, apply it
    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        user_collection = user_collection.filter(album__artist__name=artist_filter)

    return render(request, 'collection/album_overview.html', {
        'user_collection': user_collection,
        'user_album_ids': user_album_ids,
        'artist_list': artist_list,
    })

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