import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import subprocess

# Retrieving credentials from .env
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Authentication through Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Create your views here.
@csrf_exempt  # Disable CSRF validation for this view
def update_repo(request):
    if request.method == 'POST':
        # Set your GitHub username and personal access token
        github_username = 'HonHonX'
        github_token = config('GITHUB_TOKEN')

        # Change to repo
        repo_path = '/home/WTCollectionTracker/Collection-Tracker/collectionTracker/'
        os.chdir(repo_path)

        # Select branch to pull from
        branch_name = 'DjangoWebhook'

        # Pull the latest changes using the token
        result = subprocess.call(['git', 'pull', f'https://{github_username}:{github_token}@github.com/HonHonX/Collection-Tracker.git', branch_name])
        
        logger.info("Git pull result: %d", result)

        return JsonResponse({'status': 'success'})
    
    logger.warning("Request method not allowed: %s", request.method)
    return JsonResponse({'status': 'error'}, status=400)


def index(request):
    return HttpResponse("Neue Testseite unter /search 👩‍💻✨")

# View for searching artist and displaying albums
def artist_search(request):
    albums = []
    error = None
    
    if request.method == 'POST':
        artist_name = request.POST.get('artist_name')
        
        try:
            # Search by name
            result = sp.search(q=artist_name, type='artist')
            
            if len(result['artists']['items']) == 0:
                error = f"Artist {artist_name} not found!"
            else:
                # Get artist's Spotify ID
                artist_id = result['artists']['items'][0]['id']
                
                # Get all albums for the artist using the artist ID
                album_results = sp.artist_albums(artist_id=artist_id, album_type='album, single')
                
                for album in album_results['items']:
                    # Fetch album details including the cover image
                    albums.append({
                        'name': album['name'],
                        'release_date': album['release_date'],
                        'total_tracks': album['total_tracks'],
                        'url': album['external_urls']['spotify'],
                        'image_url': album['images'][0]['url'] if album['images'] else None,
                        'spotify_id': album['id'],
                    })
        except Exception as e:
            error = str(e)
    
    return render(request, 'tracker/artist_search.html', {
        'albums': albums,
        'artist_name': request.POST.get('artist_name', ''),
        'error': error,
    })
