import os
import requests

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
PLAYLIST_ID = "3x5cph0HOhJXp7ZGd0nCDx"  # Pinguin Graadmeter

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data,
                             auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET))
    if response.status_code != 200:
        raise Exception(f"❌ Kon geen token ophalen. Status: {response.status_code}, Antwoord: {response.text}")
    return response.json()["access_token"]

def get_artists_from_playlist(token):
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    try:
        data = response.json()
    except Exception as e:
        print("❌ Kan geen JSON parseren:", e)
        print("Statuscode:", response.status_code)
        print("Response tekst:", response.text)
        raise

    # 🔍 Debug: toon volledige JSON response
    print("📦 Volledige response JSON:")
    print(data)

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
    print(f"🎤 Artiesten in de playlist: {artists}")

if __name__ == "__main__":
    main()
