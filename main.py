import os
import requests
import smtplib
from email.mime.text import MIMEText

BANDSINTOWN_APP_ID = "graadmeter-alerts"
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_TO = os.getenv("MAIL_TO")

def get_graadmeter_artists():
    url = "https://pinguinradio.com/graadmeter"
    resp = requests.get(url)
    resp.raise_for_status()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")
    artists = [a.text.strip() for a in soup.select(".graadmeter-list a")]
    return artists

def get_concerts(artist):
    url = f"https://rest.bandsintown.com/artists/{artist}/events?app_id={BANDSINTOWN_APP_ID}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    events = resp.json()
    if isinstance(events, dict) and events.get("error"):
        return []
    return events

def create_email_body(concerts_dict):
    lines = []
    for artist, events in concerts_dict.items():
        if not events:
            continue
        lines.append(f"<h3>{artist}</h3>")
        for event in events:
            date = event.get("datetime", "Onbekende datum")
            venue = event.get("venue", {}).get("name", "Onbekende locatie")
            city = event.get("venue", {}).get("city", "")
            country = event.get("venue", {}).get("country", "")
            url = event.get("url", "#")
            lines.append(f"<p>{date[:10]} - {venue} ({city}, {country}) - <a href='{url}'>Tickets</a></p>")
    return "<br>".join(lines) if lines else "<p>Geen concerten gevonden.</p>"

def send_mail(subject, html_body):
    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, MAIL_FROM, MAIL_TO]):
        print("Mailgun gegevens niet compleet ingesteld.")
        return
    import requests
    resp = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": MAIL_FROM,
            "to": MAIL_TO,
            "subject": subject,
            "html": html_body
        }
    )
    if resp.status_code == 200:
        print("E-mail succesvol verzonden!")
    else:
        print(f"Fout bij verzenden e-mail: {resp.text}")

def main():
    artists = get_graadmeter_artists()
    concerts = {}
    for artist in artists:
        events = get_concerts(artist)
        concerts[artist] = events
    body = create_email_body(concerts)
    send_mail("Wekelijkse Graadmeter Concerten", body)

if __name__ == "__main__":
    main()