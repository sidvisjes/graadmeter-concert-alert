import smtplib
from email.message import EmailMessage
import os

# Zet deze eventueel hardcoded om te testen
SMTP_USER ="postmaster@sandbox4310c577257a42ba9932bc55e335514a.mailgun.org"
SMTP_PASSWORD = "1ce77a6efc563b1881ac29cb0c602be2-51afd2db-0e23a016"
MAIL_TO = "jan@knoops.org"

msg = EmailMessage()
msg["Subject"] = "✅ Testmail via Mailgun SMTP"
msg["From"] = SMTP_USER
msg["To"] = MAIL_TO
msg.set_content("Dit is een testmail verstuurd via smtp.mailgun.org met poort 465 en SSL.")

try:
    with smtplib.SMTP_SSL("smtp.mailgun.org", 465) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)
        print("✅ Testmail verzonden!")
except Exception as e:
    print("❌ Fout bij verzenden testmail:", e)
