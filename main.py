import smtplib
import os
import requests
from email.message import EmailMessage
from urllib.parse import quote

BANDSINTOWN_APP_ID = "graadmeter-concert-alert"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_PLAYLIST_ID = "7FiA9odZSTMLVgEGlL4yKJ"  # Graadmeter playlist
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

def get_spotify_token():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=10
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    return token

def get_artists_from_spotify(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{SPOTIFY_API_BASE}/playlists/{SPOTIFY_PLAYLIST_ID}/tracks"
    artists = set()
    while url:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        for item in data["items"]:
            track = item.get("track")
            if track and track.get("artists"):
                for artist in track["artists"]:
                    artists.add(artist["name"])
        url = data.get("next")  # paginate
    artist_list = list(artists)
    print(f"🎤 Artiesten van Spotify Graadmeter: {artist_list}")
    return artist_list

def search_artist_official_name(artist_name):
    url = f"https://rest.bandsintown.com/search/artists?query={quote(artist_name)}&app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Zoekfout voor {artist_name}: status {response.status_code}")
            return None
        data = response.json()
        if not data:
            print(f"⚠️ Geen zoekresultaten voor {artist_name}")
            return None
        official_name = data[0].get("name")
        print(f"🔎 '{artist_name}' gevonden als officiële naam: '{official_name}'")
        return official_name
    except Exception as e:
        print(f"❌ Exception bij zoeken artiest {artist_name}: {e}")
        return None

def get_concerts(artist_name):
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
