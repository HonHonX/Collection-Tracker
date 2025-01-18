import requests
from decouple import config

release_id = 96559  # Example release ID
url = f"https://api.discogs.com/releases/{release_id}"

token = config('DISCOGS_TOKEN')
headers = {
    "User-Agent": "YourApp/1.0",
    "Authorization": "Discogs token={token}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    release_data = response.json()
else:
    print(f"Error: {response.status_code}")
