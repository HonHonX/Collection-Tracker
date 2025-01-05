from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Add this import
from collection.models import UserProgress, Genre, UserAlbumCollection, Artist, UserArtistProgress, Album
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField, IntegerField

@login_required
def dashboard_view(request):
    user = request.user
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

    # Calculate ranking of users and their friends based on collection size
    user_and_friends = User.objects.filter(
        Q(id=user.id) | Q(useralbumcollection__album__useralbumcollection__user=user)
    ).annotate(
        collection_size=Count('useralbumcollection__album')
    ).order_by('-collection_size')

    # Add user icons for each user in the ranking
    for ranked_user in user_and_friends:
        ranked_user.icon_url = ranked_user.profile.image.url if ranked_user.profile.image else None

    context = {
        'user_progress': user_progress,
        'top_genres': top_genres,
        'top_artists': top_artists,
        'top_quality_artists': top_quality_artists,
        'top_friends': top_friends,
        'user_and_friends': user_and_friends,
    }
    return render(request, 'stats/dashboard.html', context)


