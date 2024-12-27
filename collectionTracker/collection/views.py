from django.shortcuts import render
from django.views import View    
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Album, UserAlbumCollection
from django.contrib.auth.decorators import login_required

# Create your views here.
    
class album_detail(View):
    def get(self, request):  
        return render(request, 'collection/album_detail.html')   
    
@csrf_exempt
def add_album_to_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})

        # Get or create the album
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
        try:
            collection_entry = UserAlbumCollection.objects.get(user=user, album=album)
            return JsonResponse({
                'success': False,
                'message': f'Album "{album.name}" is already in your collection.',
                'added_on': collection_entry.added_on.strftime('%Y-%m-%d %H:%M:%S')
            })
        except UserAlbumCollection.DoesNotExist:
            # Add to collection if not present
            UserAlbumCollection.objects.create(user=user, album=album)
            return JsonResponse({'success': True, 'message': f'Album "{album.name}" added to your collection!'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@csrf_exempt
@login_required
def remove_album_from_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        user = request.user

        # Check if the album exists in the user's collection
        try:
            collection_entry = UserAlbumCollection.objects.get(user=user, album__id=album_id)
            collection_entry.delete()  # Remove the album from the collection
            return JsonResponse({'success': True, 'message': f'Album with ID "{album_id}" removed from your collection.'})
        except UserAlbumCollection.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found in your collection.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def album_overview(request):
    # Fetch the albums that the user has added to their collection
    user_collection = UserAlbumCollection.objects.filter(user=request.user)
    # Extract album IDs into a list
    user_album_ids = list(user_collection.values_list('album__id', flat=True))
    
    # Pass the collection and album IDs to the template
    return render(request, 'collection/album_overview.html', {
        'user_collection': user_collection,
        'user_album_ids': user_album_ids,
    })