# integration/urls.py
from django.urls import path
from .discogs_query import get_artist_data  # Correct the import

urlpatterns = [
    path('test-discogs/', get_artist_data, name='get_artist_data'),  # Correct the reference
]