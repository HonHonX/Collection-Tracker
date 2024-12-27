from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
import json
from .models import Artist, Album, UserAlbumCollection

# View for rendering the artist overview page
@login_required
def artist_overview(request, artist_id):
    # Fetch the artist by ID or return a 404 if not found
    artist = get_object_or_404(Artist, id=artist_id)
    
    # Fetch all albums for this artist
    albums = Album.objects.filter(artist=artist)
    
    # Prepare context data for the template
    context = {
        'artist_name': artist.name,
        'artist_photo_url': artist.photo_url,
        'artist_info': {
            'genres': artist.genres,
            'popularity': artist.popularity,
            'total_albums': albums.count(),
        },
        'albums': albums,
        'latest_album': albums.order_by('-release_date').first(),  # Latest album by release date
    }
    
    return render(request, 'artist_overview.html', context)

# View for rendering the user's album collection overview page
@login_required
def album_overview(request):
    # Get all albums in the user's collection
    user_collection = UserAlbumCollection.objects.filter(user=request.user)
    
    # Extract album IDs for quick lookup in templates
    user_album_ids = list(user_collection.values_list('album__id', flat=True))
    
    return render(request, 'album_overview.html', {
        'user_collection': user_collection,
        'user_album_ids': user_album_ids,
    })

# API endpoint to add an album to the user's collection (AJAX request)
@csrf_exempt
def add_album_to_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse JSON request body
        album_id = data.get('album_id')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})

        # Get or create the album instance
        album, _ = Album.objects.get_or_create(
            id=album_id,
            defaults={
                'name': data.get('album_name'),
                'album_type': data.get('album_type'),
                'release_date': data.get('release_date'),
                'image_url': data.get('image_url'),
            }
        )

        # Check if the album is already in the user's collection
        if UserAlbumCollection.objects.filter(user=user, album=album).exists():
            return JsonResponse({
                'success': False,
                'message': f'Album "{album.name}" is already in your collection.'
            })

        # Add the album to the user's collection
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

# Example view for rendering a detailed page for a single album (optional)
class AlbumDetailView(View):
    def get(self, request):
        return render(request, 'collection/album_detail.html')
