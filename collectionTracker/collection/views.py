from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Album, Artist, UserAlbumCollection, UserAlbumDescription, UserAlbumWishlist, UserAlbumBlacklist
import json
from django.db import IntegrityError


# Helper functions
def get_user_album_ids(user):
    """Returns album IDs for the user's collection and wishlist."""
    user_collection = UserAlbumCollection.objects.filter(user=user)
    user_wishlist = UserAlbumWishlist.objects.filter(user=user)
    user_blacklist = UserAlbumBlacklist.objects.filter(user=user)

    user_album_ids = list(user_collection.values_list('album__id', flat=True))
    user_wishlist_ids = list(user_wishlist.values_list('album__id', flat=True))
    user_blacklist_ids = list(user_blacklist.values_list('album__id', flat=True))

    return user_album_ids, user_wishlist_ids, user_blacklist_ids, user_collection, user_wishlist, user_blacklist


def get_artist_list(user):
    """Returns a list of unique artists from the user's collection."""
    return Artist.objects.filter(album__useralbumcollection__user=user).distinct()

def manage_album_in_list(user, album, list_type, action):
    """
    Add or remove an album to/from the specified list (collection/wishlist) for the given user.
    :param user: User instance
    :param album: Album instance
    :param list_type: Type of the list ('collection', 'wishlist')
    :param action: Action to perform ('add' or 'remove')
    :return: JsonResponse indicating success or failure
    """
    if list_type == 'collection':
        model = UserAlbumCollection
    elif list_type == 'wishlist':
        model = UserAlbumWishlist
    elif list_type == 'blacklist':
        model = UserAlbumBlacklist
    else:
        return JsonResponse({'success': False, 'error': 'Invalid list type.'})
    
    if action == 'add':
        try:
            model.objects.create(user=user, album=album)
            return JsonResponse({'success': True, 'message': f'Album "{album.name}" added to your {list_type}.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'message': f'Album "{album.name}" is already in your {list_type}.'})
    
    elif action == 'remove':
        try:
            entry = model.objects.get(user=user, album=album)
            entry.delete()
            return JsonResponse({'success': True, 'message': f'Album "{album.name}" removed from your {list_type}.'})
        except model.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Album not found in your {list_type}.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid action.'})

# Views

# Sammlung
@login_required
def album_overview(request):
    user_album_ids, user_wishlist_ids, user_blacklist_ids, user_collection, user_wishlist, user_blacklist = get_user_album_ids(request.user)

    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        user_collection = user_collection.filter(album__artist__name=artist_filter)

    artist_list = get_artist_list(request.user)

    return render(request, 'collection/album_overview.html', {
        'user_blacklist': user_blacklist,
        'user_blacklist_ids': user_blacklist_ids,
        'user_wishlist': user_wishlist,
        'user_wishlist_ids': user_wishlist_ids,
        'user_album_ids': user_album_ids,
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

        artist, _ = Artist.objects.get_or_create(name=artist_name)
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

        # Use the generic function to handle album addition to the collection
        return manage_album_in_list(user, album, 'collection', 'add')

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@csrf_exempt
@login_required
def remove_album_from_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        user = request.user
        
        try:
            album = Album.objects.get(id=album_id)
            # Use the generic function to handle album removal from the collection
            return manage_album_in_list(user, album, 'collection', 'remove')
        except Album.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# Wishlist
@login_required
def wishlist_overview(request):
    user_album_ids, user_wishlist_ids, user_blacklist_ids, user_collection, user_wishlist, user_blacklist = get_user_album_ids(request.user)

    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        user_wishlist = user_wishlist.filter(album__artist__name=artist_filter)

    artist_list = get_artist_list(request.user)

    return render(request, 'collection/wishlist_overview.html', {
        'user_blacklist': user_blacklist,
        'user_blacklist_ids': user_blacklist_ids,
        'user_wishlist': user_wishlist,
        'user_wishlist_ids': user_wishlist_ids,
        'user_album_ids': user_album_ids,
        'artist_list': artist_list,
    })

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

        artist, _ = Artist.objects.get_or_create(name=artist_name)
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

        # Use the generic function to handle album addition to the wishlist
        return manage_album_in_list(user, album, 'wishlist', 'add')

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@csrf_exempt
@login_required
def remove_album_from_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        user = request.user
        
        try:
            album = Album.objects.get(id=album_id)
            # Use the generic function to handle album removal from the wishlist
            return manage_album_in_list(user, album, 'wishlist', 'remove')
        except Album.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# Blacklist
@login_required
def blacklist_overview(request):
    user_album_ids, user_wishlist_ids, user_blacklist_ids, user_collection, user_wishlist, user_blacklist = get_user_album_ids(request.user)

    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        user_blacklist = user_blacklist.filter(album__artist__name=artist_filter)

    artist_list = get_artist_list(request.user)

    return render(request, 'collection/blacklist_overview.html', {
        'user_blacklist': user_blacklist,
        'user_blacklist_ids': user_blacklist_ids,
        'user_wishlist': user_wishlist,
        'user_wishlist_ids': user_wishlist_ids,
        'user_album_ids': user_album_ids,
        'artist_list': artist_list,
    })

@csrf_exempt
@login_required
def add_album_to_blacklist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        artist_name = data.get('artist_name')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})

        artist, _ = Artist.objects.get_or_create(name=artist_name)
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

        # Use the generic function to handle album addition to the wishlist
        return manage_album_in_list(user, album, 'blacklist', 'add')

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@csrf_exempt
@login_required
def remove_album_from_blacklist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        album_id = data.get('album_id')
        user = request.user
        
        try:
            album = Album.objects.get(id=album_id)
            # Use the generic function to handle album removal from the blacklist
            return manage_album_in_list(user, album, 'blacklist', 'remove')
        except Album.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


# Album Detail
class AlbumDetail(View):
    def get(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)
        in_collection = UserAlbumCollection.objects.filter(user=request.user, album=album).exists()
        in_wishlist = UserAlbumWishlist.objects.filter(user=request.user, album=album).exists()

        user_description = UserAlbumDescription.objects.filter(user=request.user, album=album).first() if request.user.is_authenticated else None

        context = {
            'album': album,
            'artist': album.artist,
            'in_collection': in_collection,
            'in_wishlist': in_wishlist,
            'user_description': user_description,
        }

        return render(request, 'collection/album_detail.html', context)

    def post(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)

        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=403)

        description = request.POST.get('description', '').strip()
        if not description:
            return JsonResponse({'success': False, 'error': 'Description cannot be empty'}, status=400)

        user_description, created = UserAlbumDescription.objects.get_or_create(user=request.user, album=album)
        user_description.description = description
        user_description.save()

        return JsonResponse({'success': True, 'message': 'Description updated successfully'}, status=200)
    
# Add/Edit Description
@login_required
def save_description(request, album_id):
    if request.method == "POST" and request.user.is_authenticated:
        description = request.POST.get('description')

        try:
            album = Album.objects.get(id=album_id)
            user_description, created = UserAlbumDescription.objects.get_or_create(
                user=request.user,
                album=album,
            )

            user_description.description = description
            user_description.save()

            return JsonResponse({'success': True})

        except Album.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method or user not authenticated'})