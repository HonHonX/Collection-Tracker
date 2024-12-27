from django.shortcuts import render, get_object_or_404
from django.views import View
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Album, Artist, UserAlbumCollection

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

class AlbumDetail(View):
    """Zeigt die Details eines Albums."""
    def get(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)
        context = {
            'album': album,
            'artist': album.artist,
        }
        return render(request, 'collection/album_detail.html', context)

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
    user_collection = UserAlbumCollection.objects.filter(user=request.user)
    user_album_ids = list(user_collection.values_list('album__id', flat=True))
    artist_data = [
        {
            "name": entry.album.artist.name,
            "photo_url": entry.album.artist.photo_url,
            "genres": entry.album.artist.genres,
            "popularity": entry.album.artist.popularity,
        }
        for entry in user_collection
    ]
    return render(request, 'collection/album_overview.html', {
        'user_collection': user_collection,
        'user_album_ids': user_album_ids,
        'artist_data': artist_data,
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


