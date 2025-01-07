from django.http import JsonResponse
from collection.models import Artist, UserAlbumCollection, UserAlbumWishlist, UserAlbumBlacklist

# Artist - helper functions
def get_artist_list(user):
    """
    Returns a list of unique artists from the user's collection.
    
    Args:
        user (User): The user object.
    
    Returns:
        QuerySet: A queryset of unique artists.
    """
    try:
        # Retrieve the list of artists from the user's collection
        return Artist.objects.filter(album__useralbumcollection__user=user).distinct()
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Collection/Wishlist/Blacklist - helper functions
def get_user_album_ids(user):
    """
    Returns album IDs for the user's collection, wishlist, and blacklist.
    
    Args:
        user (User): The user object.
    
    Returns:
        tuple: A tuple containing lists of album IDs and querysets for collection, wishlist, and blacklist.
    """
    try:
        # Retrieve the user's album collection, wishlist, and blacklist from the database
        user_collection = UserAlbumCollection.objects.filter(user=user)
        user_wishlist = UserAlbumWishlist.objects.filter(user=user)
        user_blacklist = UserAlbumBlacklist.objects.filter(user=user)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return (
        list(user_collection.values_list('album__id', flat=True)),
        list(user_wishlist.values_list('album__id', flat=True)),
        list(user_blacklist.values_list('album__id', flat=True)),
        user_collection,
        user_wishlist,
        user_blacklist,
    )
    
def manage_album_in_list(user, album, list_type, action):
    """
    Add or remove an album to/from the specified list (collection/wishlist/blacklist) for the given user.
    
    Args:
        user (User): The user object.
        album (Album): The album object.
        list_type (str): The type of the list (collection, wishlist, or blacklist).
        action (str): The action to perform (add or remove).
    
    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        # Retrieve the album list model based on the provided list type
        list_model = get_album_list_model(list_type)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)})

    if action == 'add':
        return add_album_to_list(user, album, list_model)
    elif action == 'remove':
        return remove_album_from_list(user, album, list_model)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid action.'})
    
def add_album_to_list(user, album, model):
    """
    Helper function to add an album to the specified list.
    
    Args:
        user (User): The user object.
        album (Album): The album object.
        model (Model): The model class representing the list.
    
    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        model.objects.create(user=user, album=album)
        return JsonResponse({'success': True, 'message': f'Album "{album.name}" added to your {model.__name__}.'})
    except IntegrityError:
        return JsonResponse({'success': False, 'message': f'Album "{album.name}" is already in your {model.__name__}.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def remove_album_from_list(user, album, model):
    """
    Helper function to remove an album from the specified list.
    
    Args:
        user (User): The user object.
        album (Album): The album object.
        model (Model): The model class representing the list.
    
    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        entry = model.objects.get(user=user, album=album)
        entry.delete()
        return JsonResponse({'success': True, 'message': f'Album "{album.name}" removed from your {model.__name__}.'})
    except model.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'Album not found in your {model.__name__}.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
def get_album_list_model(list_type):
    """
    Helper function to retrieve the album list model based on the provided list type.
    
    Args:
        list_type (str): The type of the list (collection, wishlist, or blacklist).
    
    Returns:
        Model: The model class representing the list.
    
    Raises:
        ValueError: If the list type is invalid.
    """
    model_map = {
        'collection': UserAlbumCollection,
        'wishlist': UserAlbumWishlist,
        'blacklist': UserAlbumBlacklist,
    }
    list_model = model_map.get(list_type)
    if not list_model:
        raise ValueError('Invalid list type.')
    return list_model

def filter_list_by_artist(request, list_type):
    """
    Helper function to filter the list_type (Collection/Wishlist/Blacklist) by artist.
    
    Args:
        request (HttpRequest): The HTTP request object.
        list_type (QuerySet): The queryset representing the list.
    
    Returns:
        QuerySet: The filtered queryset.
    """
    artist_filter = request.GET.get('artist', '')
    if artist_filter:
        list_type = list_type.filter(album__artist__name=artist_filter)
    return list_type