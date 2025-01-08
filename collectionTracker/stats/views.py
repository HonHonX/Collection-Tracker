import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from friends.models import Friend
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField, IntegerField
from django.http import JsonResponse
from django.contrib import messages
from collection.models import UserProgress, Genre, UserAlbumCollection, Artist, UserArtistProgress, Album
from utils.stats_helpers import (
    calculate_top_genres,
    calculate_top_artists,
    calculate_top_quality_artists,
    calculate_top_friends,
    calculate_user_and_friends_ranking,
    calculate_user_rank_for_artist
)
from .signals import badge_awarded

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    """
    Render the dashboard view with user progress, top genres, top artists, top quality artists, top friends, and user rank.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered dashboard view.
    """
    user = request.user
    selected_artist_id = request.GET.get('selected_artist_id')
    user_rank = None
    users_with_more_albums = 0
    selected_artist = None
    artist_list = Artist.objects.filter(album__useralbumcollection__user=user).distinct()
    
    try:
        user_progress = UserProgress.objects.get(user=user)
    except UserProgress.DoesNotExist:
        user_progress = UserProgress.objects.create(user=user)

    top_genres = calculate_top_genres(user)
    top_artists = calculate_top_artists(user)
    top_quality_artists = calculate_top_quality_artists(user)
    top_friends = calculate_top_friends(user)
    
    friends = Friend.objects.filter(user=user, status='accepted').values_list('friend_email', flat=True)
    friends_users = User.objects.filter(email__in=friends)
    user_and_friends = calculate_user_and_friends_ranking(user, friends_users)

    if selected_artist_id:
        user_rank, selected_artist, users_with_more_albums = calculate_user_rank_for_artist(user, selected_artist_id)

    context = {
        'user_progress': user_progress,
        'top_genres': top_genres,
        'top_artists': top_artists,
        'top_quality_artists': top_quality_artists,
        'top_friends': top_friends,
        'user_and_friends': user_and_friends,
        'artist_list': artist_list,
        'user_rank': user_rank,
        'selected_artist_id': selected_artist_id,
        'selected_artist': selected_artist,
        'users_with_more_albums': users_with_more_albums,
    }
    return render(request, 'stats/dashboard.html', context)

@login_required
def get_user_progress(request):
    """
    Get the user's overall progress and album states.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the user's progress and album states.
    """
    user = request.user
    try:
        # Get the user's overall progress
        user_progress = UserProgress.objects.get(user=user)
        # Get the album states (collection, wishlist, blacklist)
        album_states = {
            album.album.id: {
                'inCollection': album.album.id in user_progress.collection,
                'inWishlist': album.album.id in user_progress.wishlist,
                'inBlacklist': album.album.id in user_progress.blacklist
            }
            for album in Album.objects.all()  # Adjust as per your requirements
        }
         
        # Return the user progress data
        return JsonResponse({
            'success': True,
            'progress': {
                'totalAlbums': user_progress.total_albums,
                'total_collection_count': user_progress.total_collection_count,
                'total_collection_and_wishlist_count': user_progress.total_collection_and_wishlist_count,
                'total_wishlist_count': user_progress.total_wishlist_count,
                'total_blacklist_count': user_progress.total_blacklist_count
            },
            'albumStates': album_states,
            'badge_awarded': "You've earned a new badge!"  # Add this line
        })

    except UserProgress.DoesNotExist:
        logger.error('UserProgress does not exist for user: %s', user.username)
        return JsonResponse({'success': False, 'error': 'Progress data not found.'})
