# Graadmeter Concert Alert

Dit project checkt wekelijks de artiesten van de Pinguin Radio Graadmeter op concerten via Bandsintown
en stuurt daarover een e-mail via Mailgun.

## Setup

1. Maak een nieuwe GitHub repository aan (bijv. `graadmeter-concert-alert`).
2. Push alle bestanden uit deze map naar je repository.
3. Ga in je GitHub repo naar **Settings > Secrets** en voeg de volgende secrets toe:

   - `MAILGUN_API_KEY`: je Mailgun API key
   - `MAILGUN_DOMAIN`: je Mailgun domein (bijv. sandbox)
   - `MAIL_FROM`: het e-mailadres dat je gebruikt als afzender (Mailgun)
   - `MAIL_TO`: het e-mailadres waar de mails naartoe gestuurd worden

4. Ga naar het tabblad **Actions** en start de workflow handmatig door te klikken op **Run workflow**.

## Benodigdheden

- Python 3.x
- GitHub Actions
- Mailgun account met sandbox domein (of eigen domein)