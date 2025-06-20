import smtplib
import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from urllib.parse import quote

BANDSINTOWN_APP_ID = "graadmeter-concert-alert"

def get_artists():
    url = "https://pinguinradio.com/graadmeter"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    artist_elements = soup.select(".field-content a")
    artists = [a.text.strip() for a in artist_elements if a.text.strip()]
    print(f"🎤 Aantal artiesten gevonden: {len(artists)}")
    return list(set(artists))

def get_events_by_artist_name(artist_name):
    """Probeer eerst events direct op artiestnaam."""
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Fout bij ophalen events voor {artist_name}: status {response.status_code}")
            return []
        data = response.json()
        if isinstance(data, dict) and data.get('error'):
            print(f"⚠️ Error van API voor {artist_name}: {data.get('error')}")
            return []
        return data if
