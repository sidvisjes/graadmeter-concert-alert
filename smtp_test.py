import smtplib
import os
from email.message import EmailMessage

smtp_user = os.environ.get("SMTP_USER")
smtp_password = os.environ.get("SMTP_PASSWORD")
mail_to = os.environ.get("MAIL_TO")

if not all([smtp_user, smtp_password, mail_to]):
    raise Exception("SMTP_USER, SMTP_PASSWORD of MAIL_TO ontbreekt in de environment")

msg = EmailMessage()
msg["Subject"] = "✅ Mailgun SMTP-test geslaagd"
msg["From"] = smtp_user
msg["To"] = mail_to
msg.set_content("Dit is een testmail via Mailgun SMTP vanaf GitHub Actions.")

try:
    with smtplib.SMTP("smtp.mailgun.org", 587) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)
        print("✅ Testmail succesvol verzonden!")
except Exception as e:
    print("❌ Fout bij verzenden testmail:", e)
