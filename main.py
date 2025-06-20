import smtplib
import os
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage

BANDSINTOWN_APP_ID = "graadmeter-concert-alert"

def get_artists():
    url = "https://pinguinradio.com/graadmeter"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    artist_elements = soup.select(".field-content a")
    artists = [a.text.strip() for a in artist_elements if a.text.strip()]
    return list(set(artists))  # Uniek maken

def get_concerts(artist):
    url = f"https://rest.bandsintown.com/artists/{requests.utils.quote(artist)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        data = response.json()
        return [
            {
                "artist": artist,
                "venue": event["venue"]["name"],
                "city": event["venue"]["city"],
                "datetime": event["datetime"][:10],
                "url": event.get("url", "")
            }
            for event in data if event["venue"]["country"] == "Netherlands"
        ]
    except Exception as e:
        print(f"Fout bij ophalen concerten voor {artist}: {e}")
        return []

def format_email_content(concerts):
    if not concerts:
        return "Geen concerten gevonden in Nederland voor artiesten uit de Pinguin Graadmeter."

    lines = ["🎸 Concertalert – Pinguin Graadmeter 🎶", ""]
    for concert in con
