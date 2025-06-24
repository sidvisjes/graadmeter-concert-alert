import os
import requests
from urllib.parse import quote

BANDSINTOWN_APP_ID = "graadmeter-concert-alert"

def get_events_for_artist(artist_name):
    url = f"https://rest.bandsintown.com/artists/{quote(artist_name)}/events?app_id={BANDSINTOWN_APP_ID}"
    print(f"Opvragen events voor: {artist_name}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Statuscode: {response.status_code}")
        if response.status_code != 200:
            print(f"Fout bij ophalen: {response.text}")
            return []
        data = response.json()
        if not data or (isinstance(data, dict) and data.get("error")):
            print(f"Geen events voor {artist_name}")
            return []
        print(f"Events voor {artist_name}:")
        for event in data:
            print(f"- {event.get('venue', {}).get('name', '')} in {event.get('venue', {}).get('city', '')} op {event.get('datetime', '')}")
        return data
    except Exception as e:
        print(f"Exception bij ophalen events: {e}")
        return []

def main():
    # Vervang hier met een bekende artiest waar je zeker concerten van verwacht
    test_artists = [
        "The Claw Boys Claw",
        "Fontaines D.C.",
        "Radiohead"
    ]

    for artist in test_artists:
        get_events_for_artist(artist)
        print("---")

if __name__ == "__main__":
    main()
