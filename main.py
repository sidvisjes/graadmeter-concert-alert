import smtplib
import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from urllib.parse import quote
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BANDSINTOWN_APP_ID = "graadmeter-concert-alert"

def get_artists():
    url = "https://pinguinradio.com/graadmeter"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        artist_elements = soup.select(".field-content a")
        artists = [a.text.strip() for a in artist_elements if a.text.strip()]
        if not artists:
            logging.warning("⚠️ Geen artiesten gevonden via scraping, gebruik fallback.")
            return ["S10", "Froukje", "De Staat", "Chef'Special"]
        logging.info(f"🎤 Artiesten van de graadmeter: {artists}")
        return list(set(artists))
    except Exception as e:
        logging.error(f"❌ Fout bij ophalen artiestenpagina: {e}")
        return ["S10", "Froukje", "De Staat", "Chef'Special"]

def search_artist_official_name(artist_name):
    url = f"https://rest.bandsintown.com/search/artists?query={quote(artist_name)}&app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logging.error(f"❌ Zoekfout voor {artist_name}: status {response.status_code}")
            return None
        data = response.json()
        if not data:
            logging.warning(f"⚠️ Geen zoekresultaten voor {artist_name}")
            return None
        official_name = data[0].get("name")
        logging.info(f"🔎 '{artist_name}' gevonden als officiële naam: '{official_name}'")
        return official_name
    except Exception as e:
        logging.error(f"❌ Exception bij zoeken artiest {artist_name}: {e}")
        return None

def get_concerts(artist_name, label_artist=None):
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        logging.info(f"🌐 [{artist_name}] status: {response.status_code}")
        if response.status_code != 200:
            return []
        data = response.json()
        if not isinstance(data, list):
            logging.warning(f"⚠️ Onverwacht format voor {artist_name}: {data}")
            return []

        logging.info(f"📦 {len(data)} events gevonden voor {artist_name}")
        filtered = []
        for e in data:
            venue = e.get("venue", {})
            country = venue.get("country", "").lower()
            if "nether" in country or country == "nl":
                e["artist"] = label_artist or artist_name
                filtered.append(e)
                logging.info(f"✅ {artist_name} – {venue.get('name')} in {venue.get('city')}, {venue.get('country')}")

        if not filtered:
            logging.warning(f"⚠️ Geen NL concerten voor {artist_name}")
        return filtered
    except Exception as e:
        logging.error(f"❌ Exception bij ophalen concerten voor {artist_name}: {e}")
        return []

def format_email_content(all_concerts, no_concert_artists):
    lines = ["🎸 Concertalert – Pinguin Graadmeter 🎶", ""]

    if all_concerts:
        for concert in all_concerts:
            venue = concert.get("venue", {})
            date = concert.get("datetime", "")[:10]
            link = concert.get("url", "")
            lines.append(f"- {concert['artist']} – {venue.get('name', '')}, {venue.get('city', '')} op {date} ({link})")
    else:
        lines.append("Geen concerten gevonden in Nederland voor artiesten uit de Pinguin Graadmeter.")

    if no_concert_artists:
        lines.append("\n⚠️ Artiesten zonder concerten in Nederland:")
        for artist in no_concert_artists:
            lines.append(f"- {artist}")

    return "\n".join(lines)

def send_email(subject, content):
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    mail_to = os.environ.get("MAIL_TO")

    if not all([smtp_user, smtp_password, mail_to]):
        raise Exception("SMTP configuratie ontbreekt")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = mail_to
    msg.set_content
