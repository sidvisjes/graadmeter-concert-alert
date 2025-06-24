import smtplib
import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from urllib.parse import quote

BANDSINTOWN_APP_ID = "graadmeter-concert-alert"

def get_artists():
    url = "https://pinguinradio.com/graadmeter"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    artist_elements = soup.select(".field-content a")
    artists = [a.text.strip() for a in artist_elements if a.text.strip()]
    print(f"🎤 Artiesten van de graadmeter: {artists}")
    return list(set(artists))

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

def get_concerts(artist_name, label_artist=None):
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url, timeout=10)
        print(f"🌐 [{artist_name}] status: {response.status_code}")
        if response.status_code != 200:
            return []
        data = response.json()
        if not isinstance(data, list):
            print(f"⚠️ Onverwacht format voor {artist_name}: {data}")
            return []

        print(f"📦 {len(data)} events gevonden voor {artist_name}")
        filtered = []
        for e in data:
            venue = e.get("
