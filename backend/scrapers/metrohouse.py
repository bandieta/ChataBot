"""Scraper for Metrohouse (metrohouse.pl) — JSON API."""
import re
import requests
from .base import Listing

BASE = "https://metrohouse.pl"
API = "https://newmhapi01.metrohouse.pl/api/getProperties"
SEARCH_URL = "/na-sprzedaz/dom/-/2000000-to-PLN/700-plot-m2/100-180-m2"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ChataBot/1.0)",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": BASE,
    "Referer": BASE + "/",
}
PER_PAGE = 50


def scrape() -> list[Listing]:
    listings = []
    try:
        page = 1
        while True:
            resp = requests.post(
                API,
                params={"page": page, "perPage": PER_PAGE},
                json={"url": SEARCH_URL},
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("result", {}).get("items", [])
            if not items:
                break

            for item in items:
                try:
                    area_raw = item.get("area", "")
                    area = float(str(area_raw).replace(",", ".")) if area_raw else None

                    price_raw = re.sub(r"[^\d]", "", str(item.get("priceNumeric") or item.get("price", "")))
                    price = int(price_raw) if price_raw else None

                    alias = item.get("alias", "")
                    url = BASE + alias if alias else ""
                    if not url:
                        continue

                    city = item.get("cityName") or ""
                    district = item.get("districtName") or ""
                    location = f"{city} {district}".strip(" ,") if district else city

                    title = f"Dom {area_raw} m² – {city}" if area_raw and city else f"Dom – Metrohouse"

                    listings.append(Listing(
                        agency="Metrohouse",
                        url=url,
                        title=title,
                        location=location,
                        price=price,
                        area=area,
                        lat=item.get("lat"),
                        lng=item.get("lng"),
                    ))
                except Exception:
                    continue

            if len(items) < PER_PAGE:
                break
            page += 1

    except Exception as e:
        print(f"[Metrohouse] scraper error: {e}")
    return listings
