from django.urls import path
from stats.views import dashboard_view, get_user_progress

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('get_user_progress/', get_user_progress, name='get_user_progress'),
]
