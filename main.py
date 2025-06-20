import smtplib
import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from urllib.parse import quote
import sys

LOGFILE = "concert_alert.log"

def log(msg):
    print(msg)
    sys.stdout.flush()
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

BANDSINTOWN_APP_ID = "graadmeter-concert-alert"

def get_artists():
    url = "https://pinguinradio.com/graadmeter"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    artist_elements = soup.select(".field-content a")
    artists = [a.text.strip() for a in artist_elements if a.text.strip()]
    log(f"🎤 Artiesten van de graadmeter: {artists}")
    return list(set(artists))

def search_artist_official_name(artist_name):
    url = f"https://rest.bandsintown.com/search/artists?query={quote(artist_name)}&app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            log(f"❌ Zoekfout voor {artist_name}: status {response.status_code}")
            return None
        data = response.json()
        if not data:
            log(f"⚠️ Geen zoekresultaten voor {artist_name}")
            return None
        official_name = data[0].get("name")
        log(f"🔎 '{artist_name}' gevonden als officiële naam: '{official_name}'")
        return official_name
    except Exception as e:
        log(f"❌ Exception bij zoeken artiest {artist_name}: {e}")
        return None

def get_concerts(artist_name):
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            log(f"❌ Fout bij ophalen concerten voor {artist_name}: status {response.status_code}")
            return []
        data = response.json()
        if not data or (isinstance(data, dict) and data.get("error")):
            log(f"⚠️ Geen events voor: {artist_name}")
            return []
        filtered = [e for e in data if e.get("venue") and e["venue"].get("country") == "Netherlands"]
        if not filtered:
            log(f"⚠️ Geen events in Nederland voor: {artist_name}")
        else:
            log(f"✅ {len(filtered)} events in Nederland voor: {artist_name}")
        return filtered
    except Exception as e:
        log(f"❌ Fout bij ophalen concerten voor {artist_name}: {e}")
        return []

def format_email_content(all_concerts, no_concert_artists):
    lines = ["🎸 Concertalert – Pinguin Graadmeter 🎶", ""]

    if all_concerts:
        for concert in all_concerts:
            venue = concert.get("venue", {})
            lines.append(f"- {concert['artist']} – {venue.get('name', '')}, {venue.get('city', '')} op {concert['datetime'][:10]} ({concert.get('url', '')})")
    else:
        lines.append("Geen concerten gevonden in Nederland voor artiesten uit de Pinguin Graadmeter.")

    if no_concert_artists:
        lines.append("\n⚠️ Artiesten zonder concerten in Nederland deze week:")
        for artist in no_concert_artists:
            lines.append(f"- {artist}")

    return "\n".join(lines)

def send_email(subject, content):
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    mail_to = os.environ.get("MAIL_TO")

    if not all([smtp_user, smtp_password, mail_to]):
