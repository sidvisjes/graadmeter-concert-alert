import os
import requests
import base64
from datetime import datetime

SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

def get_spotify_token():
    auth = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    return response.json()["access_token"]

def get_artists_from_playlist(token):
    playlist_id = "3x5cph0HOhJXp7ZGd0nCDx"  # Pinguin Graadmeter
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
data = response.json()
print("🎧 Spotify Playlist Response:", data)
if "items" not in data:
    raise Exception("❌ Kan 'items' niet vinden in de Spotify-response. Check of de playlist-ID correct is en of de token werkt.")
items = data["items"]
    items = response.json()["items"]
    artist_names = set()
    for item in items:
        artists = item["track"]["artists"]
        for artist in artists:
            artist_names.add(artist["name"])
    return sorted(artist_names)

def generate_html(artists):
    lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head><meta charset='UTF-8'><title>Concerten Graadmeter</title></head>",
        "<body>",
        f"<h1>🎶 Concerten – Pinguin Graadmeter ({datetime.now().strftime('%d-%m-%Y')})</h1>",
    ]
    for artist in artists:
        slug = artist.lower().replace(" ", "+")
        lines.append(f"<h2>{artist}</h2>")
        lines.append(f"""
<iframe 
  src="https://bandsintown.com/artist/{slug}?came_from=257&utm_medium=web&utm_source=widget" 
  style="border: none; width: 100%; height: 500px;" 
  frameborder="0" 
  scrolling="no">
</iframe>
""")
    lines.append("</body></html>")
    return "\n".join(lines)

def main():
    token = get_spotify_token()
    artists = get_artists_from_playlist(token)
    html = generate_html(artists)
    with open("concerten_graadmeter.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ HTML-bestand gegenereerd: concerten_graadmeter.html")

if __name__ == "__main__":
    main()
