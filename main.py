import smtplib
import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from urllib.parse import quote

SPOTIFY_URL = "https://open.spotify.com/playlist/3x5cph0HOhJXp7ZGd0nCDx"
BANDSINTOWN_APP_ID = "graadmeter-concert-alert"

def get_artists():
    response = requests.get(SPOTIFY_URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    artists = []
    for meta in soup.select('meta[property="og:title"]'):
        title = meta.get("content", "")
        if title.lower().endswith("– de graadmeter pinguin radio"):
            artist_name = title.split("–", 1)[0].strip()
            artists.append(artist_name)
    artists = list(dict.fromkeys(artists))
    print(f"\U0001F3A4 Artiesten uit Spotify-playlist: {artists}")
    return artists

def search_artist_official_name(artist_name):
    url = f"https://rest.bandsintown.com/search/artists?query={quote(artist_name)}&app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"\u274c Zoekfout voor {artist_name}: status {response.status_code}")
            return None
        data = response.json()
        if not data:
            print(f"\u26a0\ufe0f Geen zoekresultaten voor {artist_name}")
            return None
        official_name = data[0].get("name")
        print(f"\U0001F50E '{artist_name}' gevonden als officiële naam: '{official_name}'")
        return official_name
    except Exception as e:
        print(f"\u274c Exception bij zoeken artiest {artist_name}: {e}")
        return None

def get_concerts(artist_name):
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"\u274c Fout bij ophalen concerten voor {artist_name}: status {response.status_code}")
            return []
        data = response.json()
        if not data or (isinstance(data, dict) and data.get("error")):
            print(f"\u26a0\ufe0f Geen events voor: {artist_name}")
            return []
        filtered = [e for e in data if e.get("venue") and e["venue"].get("country") == "Netherlands"]
        if not filtered:
            print(f"\u26a0\ufe0f Geen events in Nederland voor: {artist_name}")
        else:
            print(f"\u2705 {len(filtered)} events in Nederland voor: {artist_name}")
        return filtered
    except Exception as e:
        print(f"\u274c Fout bij ophalen concerten voor {artist_name}: {e}")
        return []

def format_email_content(all_concerts, no_concert_artists):
    lines = ["\U0001F3B8 Concertalert – Pinguin Graadmeter \U0001F3B6", ""]
    if all_concerts:
        for concert in all_concerts:
            venue = concert.get("venue", {})
            lines.append(f"- {concert['artist']} – {venue.get('name', '')}, {venue.get('city', '')} op {concert['datetime'][:10]} ({concert.get('url', '')})")
    else:
        lines.append("Geen concerten gevonden in Nederland voor artiesten uit de Pinguin Graadmeter.")
    if no_concert_artists:
        lines.append("\n\u26a0\ufe0f Artiesten zonder concerten in Nederland deze week:")
        for artist in no_concert_artists:
            lines.append(f"- {artist}")
    return "\n".join(lines)

def send_email(subject, content):
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    mail_to = os.environ.get("MAIL_TO")
    if not all([smtp_user, smtp_password, mail_to]):
        raise Exception("SMTP_USER, SMTP_PASSWORD of MAIL_TO ontbreekt in de environment")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = mail_to
    msg.set_content(content)
    try:
        with smtplib.SMTP("smtp.mailgun.org", 587) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_password)
            smtp.send_message(msg)
            print("\u2705 E-mail verzonden!")
    except Exception as e:
        print("\u274c Fout bij verzenden e-mail:", e)

def main():
    artists = get_artists()
    all_concerts = []
    no_concert_artists = []
    for artist in artists:
        concerts = get_concerts(artist)
        if not concerts:
            official_name = search_artist_official_name(artist)
            if official_name and official_name != artist:
                concerts = get_concerts(official_name)
                if concerts:
                    for c in concerts:
                        c["artist"] = official_name
                    all_concerts.extend(concerts)
                else:
                    no_concert_artists.append(artist)
            else:
                no_concert_artists.append(artist)
        else:
            for c in concerts:
                c["artist"] = artist
            all_concerts.extend(concerts)
    print(f"\U0001F389 Totaal concerten in NL gevonden: {len(all_concerts)}")
    print(f"\u26a0\ufe0f Artiesten zonder concerten: {no_concert_artists}")
    content = format_email_content(all_concerts, no_concert_artists)
    send_email("\U0001F3B6 Wekelijkse concertmail – Graadmeter", content)

if __name__ == "__main__":
    main()
