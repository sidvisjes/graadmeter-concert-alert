import smtplib
import os
from email.message import EmailMessage

# Haal SMTP credentials en ontvanger op uit environment variables
smtp_user = os.environ.get("SMTP_USER")
smtp_password = os.environ.get("SMTP_PASSWORD")
mail_to = os.environ.get("MAIL_TO")

print("🔍 SMTP_USER:", smtp_user)
print("🔍 MAIL_TO:", mail_to)

# Stel e-mailbericht op
msg = EmailMessage()
msg["Subject"] = "📬 Testmail van Graadmeter project"
msg["From"] = smtp_user
msg["To"] = mail_to
msg.set_content("🎶 Dit is een testmail via Mailgun SMTP, verstuurd via GitHub Actions.")

try:
    smtp_server = "smtp.mailgun.org"
    smtp_port = 587
    print("🔌 Verbinding maken met SMTP-server...")
    with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as smtp:
        print("🔐 Start TLS...")
        smtp.starttls()
        print("✅ TLS gestart")

        print("🔑 Inloggen...")
        smtp.login(smtp_user, smtp_password)
        print("✅ Ingelogd")

        print("📤 Verzenden e-mail...")
        smtp.send_message(msg)
        print("✅ E-mail succesvol verzonden!")

except Exception as e:
    print("❌ Fout bij verzenden testmail:", repr(e))
