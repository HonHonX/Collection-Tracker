from django.shortcuts import render
from django.views import View    
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Album, UserAlbumCollection
from django.contrib.auth.decorators import login_required

# Create your views here.

class album_overview(View):
    def get(self, request):  
        return render(request, 'collection/album_overview.html') 
    
class album_detail(View):
    def get(self, request):  
        return render(request, 'collection/album_detail.html')   
    
@csrf_exempt
def add_album_to_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        album_name = data.get('album_name')
        album_type = data.get('album_type')
        release_date = data.get('release_date')
        image_url = data.get('image_url')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})

        # Get or create the album
        album, _ = Album.objects.get_or_create(
            id=album_id,
            defaults={
                'name': album_name,
                'album_type': album_type,
                'release_date': release_date,
                'image_url': image_url,
            }
        )

        # Add the album to the user's collection
        collection_entry, created = UserAlbumCollection.objects.get_or_create(
            user=user,
            album=album
        )

        if created:
            return JsonResponse({'success': True, 'message': 'Album added to your collection!'})
        else:
            return JsonResponse({'success': False, 'message': 'Album already in your collection.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def user_album_collection(request):
    # Fetch the albums that the user has added to their collection
    user_collection = UserAlbumCollection.objects.filter(user=request.user)
    
    # Pass the collection to the template
    return render(request, 'collection/user_album_collection.html', {
        'user_collection': user_collection
    })