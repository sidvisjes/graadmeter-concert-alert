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
    return list(set(artists))

def get_events_by_artist_name(artist_name):
    """Probeer eerst events direct op artiestnaam."""
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fout bij ophalen events voor {artist_name}: status {response.status_code}")
            return []
        data = response.json()
        if isinstance(data, dict) and data.get('error'):
            print(f"⚠️ Error van API voor {artist_name}: {data.get('error')}")
            return []
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"❌ Exception bij ophalen events voor {artist_name}: {e}")
        return []

def search_artist_id(artist_name):
    """Fallback: zoek artiest via zoekquery, pak eerste match."""
    url = f"https://rest.bandsintown.com/search/artists?query={quote(artist_name)}&app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fout bij zoeken artiest {artist_name}: status {response.status_code}")
            return None
        data = response.json()
        if not data:
            print(f"⚠️ Geen zoekresultaten voor artiest {artist_name}")
            return None
        first = data[0]
        print(f"🔎 Fallback: '{artist_name}' gevonden als '{first.get('name')}'")
        return first.get('name')
    except Exception as e:
        print(f"❌ Exception bij zoeken artiest {artist_name}: {e}")
        return None

def get_concerts(artist_name):
    # Probeer eerst direct op naam
    events = get_events_by_artist_name(artist_name)
    if events:
        print(f"✅ Direct events gevonden voor: {artist_name}")
    else:
        print(f"⚠️ Geen events direct gevonden voor {artist_name}, probeer fallback zoeken...")
        fallback_name = search_artist_id(artist_name)
        if fallback_name and fallback_name != artist_name:
            events = get_events_by_artist_name(fallback_name)
            if events:
                print(f"✅ Events gevonden via fallback voor: {fallback_name}")
            else:
                print(f"⚠️ Geen events gevonden via fallback voor: {fallback_name}")
        else:
            print(f"⚠️ Geen fallback naam gevonden voor: {artist_name}")
    # Filter op Nederland
    filtered = [e for e in events if e.get("venue", {}).get("country") == "Netherlands"]
    if not filtered:
        print(f"⚠️ Geen events in Nederland voor: {artist_name}")
    return filtered

def format_email_content(concerts):
    if not concerts:
        return "Geen concerten gevonden in Nederland voor artiesten uit de Pinguin Graadmeter."

    lines = ["🎸 Concertalert – Pinguin Graadmeter 🎶", ""]
    for concert in concerts:
        artist = concert.get("artist", "Onbekende artiest")
        venu
