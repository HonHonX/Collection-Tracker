# views.py
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from decouple import config

def artist_recommendations(genres):
    """
    Fetch artist recommendations based on the provided genres.

    Args:
        genres (list): A list of genre names.

    Returns:
        JsonResponse: A JSON response containing a list of recommended artist names.
    """
    api_key = config('LAST_FM_API_KEY')
    url = "http://ws.audioscrobbler.com/2.0/"
    artist_names = []

    for genre in genres:

        params = {
            'method': 'tag.getTopArtists',
            'tag': genre,
            'api_key': api_key,
            'format': 'json',
            'limit': 15
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            artists = data.get('topartists', {}).get('artist', [])
            artist_names.extend([artist['name'] for artist in artists])

    artist_names = artist_names[:15]

    return JsonResponse({'artists': artist_names})

