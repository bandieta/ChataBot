import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8622852237:AAFLhUP7pAPNGPs9nzE432jMW3QHG1v-onc")
CHAT_ID = "7760838175"

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def send(listing: dict):
    area = f"{listing['area']:.0f} m²" if listing["area"] else "?"
    price = f"{listing['price']:,} zł".replace(",", " ") if listing["price"] else "?"
    text = (
        f"🏠 *Nowe ogłoszenie*\n"
        f"*{listing['title']}*\n"
        f"📍 {listing['location']}\n"
        f"📐 {area}  💰 {price}\n"
        f"🏢 {listing['agency']}\n"
        f"🔗 {listing['url']}"
    )
    try:
        resp = requests.post(API_URL, json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Telegram send error: {e}")
