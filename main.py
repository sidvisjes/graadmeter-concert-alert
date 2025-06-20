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
    return list(set(artists))  # Uniek maken

def get_concerts(artist):
    url = f"https://rest.bandsintown.com/artists/{quote(artist)}/events?app_id={BANDSINTOWN_APP_ID}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fout bij ophalen concerten voor {artist}: status {response.status_code}")
            return []
        data = response.json()
        if not data:
            print(f"⚠️ Geen events voor: {artist}")
            return []
        # Filter op Nederland
        filtered = [e for e in data if e.get("venue", {}).get("country") == "Netherlands"]
        if not filtered:
            print(f"⚠️ Geen events in Nederland voor: {artist}")
        else:
            print(f"✅ {len(filtered)} events gevonden voor: {artist}")
        return filtered
    except Exception as e:
        print(f"❌ Fout bij ophalen concerten voor {artist}: {e}")
        return []

def format_email_content(concerts):
    if not concerts:
        return "Geen concerten gevonden in Nederland voor artiesten uit de Pinguin Graadmeter."

    lines = ["🎸 Concertalert – Pinguin Graadmeter 🎶", ""]
    for concert in concerts:
        lines.append(f"- {concert['artist']} – {concert['venue']}, {concert['city']} op {concert['datetime'][:10]} ({concert.get('url', '')})")
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
            print("✅ E-mail verzonden!")
    except Exception as e:
        print("❌ Fout bij verzenden e-mail:", e)

def main():
    artists = get_artists()
    all_concerts = []
    for artist in artists:
        concerts = get_concerts(artist)
        for concert in concerts:
            concert["artist"] = artist  # Zorg dat artiestnaam ook in concert staat
        all_concerts.extend(concerts)

    content = format_email_content(all_concerts)
    send_email("🎶 Wekelijkse concertmail – Graadmeter", content)

if __name__ == "__main__":
    main()
