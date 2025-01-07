from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Add this import
from friends.models import Friend
from collection.models import UserProgress, Genre, UserAlbumCollection, Artist, UserArtistProgress, Album
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField, IntegerField
from django.http import JsonResponse

@login_required
def dashboard_view(request):
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

    # Calculate top 5 genres based on the number of albums in the user's collection
    top_genres = Genre.objects.annotate(
        album_count=Count(
            'artists__album__useralbumcollection',
            filter=Q(artists__album__useralbumcollection__user=user)
        )
    ).filter(album_count__gt=0).order_by('-album_count')[:5]

    # Add album IDs for each genre
    for genre in top_genres:
        genre.album_ids = genre.get_album_ids()

    # Calculate top 10 artists based on the number of albums in the user's collection
    top_artists = Artist.objects.annotate(
        album_count=Count(
            'album__useralbumcollection',
            filter=Q(album__useralbumcollection__user=user)
        )
    ).filter(album_count__gt=0).order_by('-album_count')[:5]

    # Calculate top 5 artists based on progress percentage excluding blacklisted albums
    top_quality_artists = UserArtistProgress.objects.filter(user=user).annotate(
        effective_total_albums=F('total_albums') - F('blacklist_count'),
        progress_percentage=ExpressionWrapper(
            (F('collection_count') + F('collection_and_wishlist_count')) * 100.0 / F('effective_total_albums'),
            output_field=FloatField()
        )
    ).order_by('-progress_percentage')[:5]

    # Calculate top 3 friends with the most similar collection
    top_friends = User.objects.filter(
        useralbumcollection__album__useralbumcollection__user=user
    ).annotate(
        common_albums=Count('useralbumcollection__album', filter=Q(useralbumcollection__album__useralbumcollection__user=user))
    ).exclude(id=user.id).order_by('-common_albums')[:3]

    # Add common albums and user icons for each friend
    for friend in top_friends:
        friend.common_album_ids = UserAlbumCollection.objects.filter(
            user=friend,
            album__useralbumcollection__user=user
        ).values_list('album__id', flat=True)
        friend.common_albums = list(Album.objects.filter(id__in=friend.common_album_ids))
        friend.icon_url = friend.profile.image.url if friend.profile.image else None

    # Retrieve all friends of the user
    friends = Friend.objects.filter(user=user, status='accepted').values_list('friend_email', flat=True)
    friends_users = User.objects.filter(email__in=friends)

    # Calculate ranking of users and their friends based on collection size
    user_and_friends = User.objects.filter(
        Q(id=user.id) | Q(id__in=friends_users)
    ).annotate(
        collection_size=Count('useralbumcollection__album')
    ).order_by('-collection_size')[:3]

    # Add user icons for each user in the ranking
    for ranked_user in user_and_friends:
        ranked_user.icon_url = ranked_user.profile.image.url if ranked_user.profile.image else None

    # Calculate user's rank for the selected artist
    if selected_artist_id:
        selected_artist = Artist.objects.get(id=selected_artist_id)
        user_album_count = UserAlbumCollection.objects.filter(user=user, album__artist=selected_artist).count()
        total_users = User.objects.filter(useralbumcollection__album__artist=selected_artist).distinct().count()
        users_with_more_albums = User.objects.filter(
            useralbumcollection__album__artist=selected_artist
        ).annotate(
            album_count=Count('useralbumcollection__album', filter=Q(useralbumcollection__album__artist=selected_artist))
        ).filter(album_count__gt=user_album_count).count()
        user_rank = (total_users - users_with_more_albums) / total_users * 100

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
            'albumStates': album_states
        })

    except UserProgress.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Progress data not found.'})
