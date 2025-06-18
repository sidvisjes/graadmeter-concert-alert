import smtplib
import os
from email.message import EmailMessage

def get_artists():
    # Simpele voorbeeldlijst — in de echte versie zou je deze scrapen van de Pinguin Graadmeter
    return [
        "Arctic Monkeys",
        "Radiohead",
        "Fontaines D.C.",
        "Wet Leg",
    ]

def format_email_content(artists):
    lines = ["🎸 Concertalert – Pinguin Graadmeter 🎶", "", "De volgende artiesten staan deze week in de lijst:"]
    for artist in artists:
        lines.append(f"- {artist}")
    lines.append("")
    lines.append("Concertinformatie is gebaseerd op Bandsintown. Meer info: https://www.bandsintown.com/")
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
    content = format_email_content(artists)
    send_email("🎶 Wekelijkse concertmail – Graadmeter", content)

if __name__ == "__main__":
    main()
