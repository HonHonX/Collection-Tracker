from django.urls import path
from stats.views import dashboard_view, get_user_progress, fetch_notifications, delete_notification, album_price_history, album_price_prognosis, save_album_price_predictions

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('get_user_progress/', get_user_progress, name='get_user_progress'),
    path('notifications/', fetch_notifications, name='fetch_notifications'),
    path('delete_notification/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('api/album/<str:album_id>/price-history/', album_price_history, name='album_price_history'),
    path('api/album/<str:album_id>/price-prognosis/', album_price_prognosis, name='album_price_prognosis'),
    path('album/<int:album_id>/save_price_predictions/', save_album_price_predictions, name='save_album_price_predictions'),
]
