import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField, IntegerField
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
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
from stats.models import Notification
from django.views.decorators.csrf import csrf_exempt
from .models import DailyAlbumPrice, AlbumPricePrediction
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pandas as pd

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

@login_required
def fetch_notifications(request):
    """
    Fetch notifications for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the notifications.
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_date')
    notifications_data = [
        {
            'id': notification.id,
            'message': notification.message,
            'created_date': notification.created_date,
            'badge_image_url': notification.user_badge.badge.image_url  # Include badge image URL
        }
        for notification in notifications
    ]
    return JsonResponse({'notifications': notifications_data})

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """
    Delete a notification for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request object.
        notification_id (int): The ID of the notification to delete.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return JsonResponse({'success': True})


@login_required
def album_price_history(request, album_id):
    prices = DailyAlbumPrice.objects.filter(album_id=album_id).order_by('date')
    data = [{'date': price.date.strftime('%Y-%m-%d'), 'price': float(price.price)} for price in prices]
    return JsonResponse(data, safe=False)

def generate_album_price_predictions(album_id):
    """
    Generate price predictions for the given album.

    Args:
        album_id (int): The ID of the album.

    Returns:
        list: A list of dictionaries containing the date and predicted price.
    """
    prices = DailyAlbumPrice.objects.filter(album_id=album_id).order_by('date')
    data = [{'date': price.date.strftime('%Y-%m-%d'), 'price': float(f"{price.price:.2f}")} for price in prices]

    if not data:
        return []

    try:
        # Data Preparation
        prognosis_data = pd.DataFrame([{'ds': item['date'], 'y': item['price']} for item in data])
        prognosis_data['ds'] = pd.to_datetime(prognosis_data['ds'])
        prognosis_data.set_index('ds', inplace=True)
    except KeyError as e:
        raise ValueError(f'Error in the data processing: {str(e)}')

    # Convert dates to ordinal
    prognosis_data['ds'] = prognosis_data.index.map(pd.Timestamp.toordinal)
    X = prognosis_data[['ds']]
    y = prognosis_data['y']

    # Create the pipeline: PolynomialFeatures -> LinearRegression
    model_pipeline = Pipeline([
        ('poly_features', PolynomialFeatures(degree=5)),
        ('linear_regression', LinearRegression())
    ])

    try:
        # Fit the model using the pipeline
        model_pipeline.fit(X, y)

        # Adjust future dates to start from tomorrow
        tomorrow = pd.Timestamp.today().normalize() + pd.Timedelta(days=1)
        future_dates = pd.date_range(start=tomorrow, periods=7, freq='D')
        future_dates_ordinal = pd.DataFrame(future_dates.map(pd.Timestamp.toordinal), columns=['ds'])
        forecast = model_pipeline.predict(future_dates_ordinal)

        forecast_data = [{'ds': date.strftime('%Y-%m-%d'), 'yhat': float(f"{price:.2f}")} for date, price in zip(future_dates, forecast)]

        if data:
            last_data_point = data[-1]
            forecast_data.insert(0, {'ds': last_data_point['date'], 'yhat': last_data_point['price']})

        return forecast_data
    
    except Exception as e:
        raise ValueError(f'Model fitting or prediction failed: {str(e)}')

@login_required
def album_price_prognosis(request, album_id):
    """
    Generate and return price predictions for the given album.

    Args:
        request (HttpRequest): The HTTP request object.
        album_id (int): The ID of the album.

    Returns:
        JsonResponse: A JSON response containing the combined data and predictions.
    """
    try:
        forecast_data = generate_album_price_predictions(album_id)
        prices = DailyAlbumPrice.objects.filter(album_id=album_id).order_by('date')
        data = [{'date': price.date.strftime('%Y-%m-%d'), 'price': float(f"{price.price:.2f}")} for price in prices]

        combined_data = data + forecast_data
        return JsonResponse(combined_data, safe=False)
    
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def save_album_price_predictions(request, album_id):
    """
    Save price predictions for the given album.

    Args:
        request (HttpRequest): The HTTP request object.
        album_id (int): The ID of the album.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        forecast_data = generate_album_price_predictions(album_id)
        album = get_object_or_404(Album, id=album_id)
        for prediction in forecast_data:
            AlbumPricePrediction.objects.update_or_create(
                album=album,
                date=prediction['ds'],
                defaults={'predicted_price': prediction['yhat']}
            )
        return JsonResponse({'success': True})
    
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=500)
