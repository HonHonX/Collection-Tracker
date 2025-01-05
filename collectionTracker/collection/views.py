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
    """Returns album IDs for the user's collection, wishlist, and blacklist."""
    user_collection = UserAlbumCollection.objects.filter(user=user)
    user_wishlist = UserAlbumWishlist.objects.filter(user=user)
    user_blacklist = UserAlbumBlacklist.objects.filter(user=user)

    return (
        list(user_collection.values_list('album__id', flat=True)),
        list(user_wishlist.values_list('album__id', flat=True)),
        list(user_blacklist.values_list('album__id', flat=True)),
        user_collection,
        user_wishlist,
        user_blacklist,
    )
 
def get_artist_list(user):
    """Returns a list of unique artists from the user's collection."""
    return Artist.objects.filter(album__useralbumcollection__user=user).distinct()

def manage_album_in_list(user, album, list_type, action):
    """
    Add or remove an album to/from the specified list (collection/wishlist/blacklist) for the given user.
    """

    print(f"List Type: {list_type}, Action: {action}")

    model_map = {
        'collection': UserAlbumCollection,
        'wishlist': UserAlbumWishlist,
        'blacklist': UserAlbumBlacklist,
    }

    model = model_map.get(list_type)
    if not model:
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
            entry_exists = model.objects.filter(user=user, album=album).exists()
            # print(f"Entry exists before deletion: {entry_exists}")
            entry.delete()
            return JsonResponse({'success': True, 'message': f'Album "{album.name}" removed from your {list_type}.'})
        except model.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Album not found in your {list_type}.'})

    return JsonResponse({'success': False, 'error': 'Invalid action.'})

# Generic album management view
@csrf_exempt 
@login_required
def manage_album(request, list_type, action):
    if request.method == 'POST':
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

        # Handle adding/removing albums from collection, wishlist, or blacklist
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

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

# Collection Overview
@login_required
def album_overview(request):
    user_album_ids, user_wishlist_ids, user_blacklist_ids, user_collection, user_wishlist, user_blacklist = get_user_album_ids(request.user)

    # print(f"Collection: {user_collection}, {user_album_ids}")

    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        user_collection = user_collection.filter(album__artist__name=artist_filter)

    artist_list = get_artist_list(request.user)

    return render(request, 'collection/album_overview.html', {
        'user_blacklist': user_blacklist,
        'user_blacklist_ids': user_blacklist_ids,
        'user_wishlist': user_wishlist,
        'user_wishlist_ids': user_wishlist_ids,
        'user_collection': user_collection,
        'user_album_ids': user_album_ids,
        'artist_list': artist_list,
    })

# Wishlist Overview
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

# Blacklist Overview
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

# Album Detail View
class AlbumDetail(View):
    def get(self, request, album_id):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        album = get_object_or_404(Album, id=album_id)
        collection_entry = UserAlbumCollection.objects.filter(user=request.user, album=album).first()
        wishlist_entry = UserAlbumWishlist.objects.filter(user=request.user, album=album).first()
        user_description = UserAlbumDescription.objects.filter(user=request.user, album=album).first()

        context = {
            'album': album,
            'artist': album.artist,
            'collection_entry': collection_entry,
            'wishlist_entry': wishlist_entry,
            'in_collection': bool(collection_entry),
            'in_wishlist': bool(wishlist_entry),
            'user_description': user_description,
            'priority_display': wishlist_entry.get_priority_display() if wishlist_entry else None,
            'substatus_display': collection_entry.get_substatus_display() if collection_entry else None,
        }

        return render(request, 'collection/album_detail.html', context)

    def post(self, request, album_id):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        album = get_object_or_404(Album, id=album_id)

        # Handle description update
        if 'description' in request.POST:
            description = request.POST.get('description', '').strip()
            user_description, created = UserAlbumDescription.objects.get_or_create(user=request.user, album=album)
            user_description.description = description or None
            user_description.save()
            return JsonResponse({'success': True, 'message': 'Description updated successfully'}, status=200)

        if 'priority' in request.POST:
            priority = request.POST.get('priority', '').strip()

            # Convert the string input to an integer
            try:
                priority = int(priority)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Priority must be a valid integer'}, status=400)

            # Ensure the priority is valid
            valid_priorities = [choice[0] for choice in UserAlbumWishlist.PRIORITY_CHOICES]
            if priority not in valid_priorities:
                return JsonResponse({'success': False, 'error': f'Invalid priority value: {priority}'}, status=400)

            # Retrieve the wishlist entry
            wishlist_entry = UserAlbumWishlist.objects.filter(user=request.user, album=album).first()
            if not wishlist_entry:
                return JsonResponse({'success': False, 'error': 'Album is not in your wishlist'}, status=400)

            # Update and save
            wishlist_entry.priority = priority
            wishlist_entry.save()

            return JsonResponse({
                'success': True,
                'message': 'Priority updated successfully',
                'priority_display': wishlist_entry.get_priority_display()
            }, status=200)


        # Handle substatus update
        if 'substatus' in request.POST:
            substatus = request.POST.get('substatus', '')
            collection_entry = UserAlbumCollection.objects.filter(user=request.user, album=album).first()
            
            valid_substatuses = [choice[0] for choice in UserAlbumCollection.SUBSTATUS]
            if substatus not in valid_substatuses:
                return JsonResponse({'success': False, 'error': 'Invalid substatus value'}, status=400)

            # Retrieve the collection entry
            collection_entry = UserAlbumCollection.objects.filter(user=request.user, album=album).first()
            if not collection_entry:
                return JsonResponse({'success': False, 'error': 'Album is not in your collection'}, status=400)

            print(f"Substatus: {substatus}")
            print(f"Collection entry: {collection_entry}")
            collection_entry.substatus = substatus
            print(f"Collection entry new: {collection_entry}")
            collection_entry.save()

            return JsonResponse({
                'success': True,
                'message': 'Substatus updated successfully',
                'substatus_display': collection_entry.get_substatus_display()
            }, status=200)

        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)    

@login_required
def save_description(request, album_id):
    if request.method == "POST":
        description = request.POST.get('description')

        try:
            album = Album.objects.get(id=album_id)
            user_description, created = UserAlbumDescription.objects.get_or_create(
                user=request.user,
                album=album,
            )

            user_description.description = description  # can be empty
            user_description.save()

            return JsonResponse({'success': True})

        except Album.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Album not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
