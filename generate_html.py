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
    response.raise_for_status()
    return response.json()["access_token"]

def get_artists_from_playlist(token):
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "items" not in data:
        raise Exception("❌ Kan 'items' niet vinden in de Spotify-response.")

    artists = set()
    for item in data["items"]:
        track = item.get("track")
        if track and "artists" in track:
            for artist in track["artists"]:
                artists.add(artist["name"])
    return sorted(artists)

def generate_html(artists):
    html = "<html><head><title>Graadmeter Artiesten</title></head><body>"
    html += "<h1>🎶 Artiesten uit de Graadmeter Playlist</h1><ul>"
    for artist in artists:
        html += f"<li>{artist}</li>"
    html += "</ul></body></html>"
    return html

def main():
    token = get_spotify_token()
    artists = get_artists_from_playlist(token)
    html = generate_html(artists)

    with open("graadmeter_artists.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ HTML-bestand succesvol aangemaakt: graadmeter_artists.html")

if __name__ == "__main__":
    main()
