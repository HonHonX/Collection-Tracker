import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from django.shortcuts import render

# Retrieve Spotify API credentials securely using decouple
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Authenticate with Spotify API using client credentials flow
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Create your views here.

def index(request):
    return HttpResponse("Möge der Code immer mit uns sein! Willkommen Janine, Marlon und Marius 👩‍💻✨")

# View for searching artist and displaying albums
def artist_search(request):
    albums = []
    error = None
    
    if request.method == 'POST':
        artist_name = request.POST.get('artist_name')
        
        try:
            # Search for the artist by name
            result = sp.search(q=artist_name, type='artist')
            
            if len(result['artists']['items']) == 0:
                error = f"Artist {artist_name} not found!"
            else:
                # Get artist's Spotify ID
                artist_id = result['artists']['items'][0]['id']
                
                # Get all albums for the artist using the artist ID
                album_results = sp.artist_albums(artist_id=artist_id, album_type='album')
                
                for album in album_results['items']:
                    # Fetch album details including the cover image
                    albums.append({
                        'name': album['name'],
                        'release_date': album['release_date'],
                        'total_tracks': album['total_tracks'],
                        'url': album['external_urls']['spotify'],
                        'image_url': album['images'][0]['url'] if album['images'] else None,  # Get the first (largest) image
                    })
        except Exception as e:
            error = str(e)
    
    return render(request, 'tracker/artist_search.html', {
        'albums': albums,
        'artist_name': request.POST.get('artist_name', ''),
        'error': error,
    })