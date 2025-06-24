import os
import base64
import requests

# Vul dit in met de juiste playlist ID van de Graadmeter
PLAYLIST_ID = "3x5cph0HOhJXp7ZGd0nCDx"

def get_spotify_token():
    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "client_credentials"}

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    if response.status_code != 200:
        print("❌ Kon geen token ophalen:", response.text)
        raise Exception("Token request failed")

    token = response.json()["access_token"]
    return token

def get_artists_from_playlist(token):
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    data = response.json()
    print("🎧 Spotify API Response:", data)

    if "items" not in data:
        raise Exception("❌ Kan 'items' niet vinden in de Spotify-response. Is de playlist-ID correct?")

    items = data["items"]

    artists = set()
    for item in items:
        track = item.get("track")
        if track and "artists" in track:
            for artist in track["artists"]:
                artists.add(artist["name"])
    return sorted(artists)

def main():
    token = get_spotify_token()
    artists = get_artists_from_playlist(token)
