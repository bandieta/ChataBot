"""Hourly scraper runner. Run this process continuously."""
import schedule
import time
import db
import notifier
import geocoder
from scrapers import get_all_scrapers

AREA_MIN = 100.0
AREA_MAX = 180.0


def run_scrapers():
    print("=== Running scrapers ===")
    scrapers = get_all_scrapers()
    for scraper in scrapers:
        try:
            listings = scraper()
            for listing in listings:
                if db.is_known(listing.url):
                    continue

                # Filter by area
                if listing.area is None or not (AREA_MIN <= listing.area <= AREA_MAX):
                    continue

                # Filter by distance from Katowice (use coords if available)
                if listing.lat and listing.lng:
                    dist = geocoder._haversine(geocoder.KATOWICE_LAT, geocoder.KATOWICE_LON, listing.lat, listing.lng)
                else:
                    dist = geocoder.distance_from_katowice(listing.location)
                if dist > geocoder.MAX_DISTANCE_KM:
                    continue

                db.insert(
                    url=listing.url,
                    agency=listing.agency,
                    title=listing.title,
                    location=listing.location,
                    price=listing.price,
                    area=listing.area,
                    distance_km=dist,
                )
                print(f"[NEW] {listing.agency}: {listing.title} | {listing.area}m² | {listing.location} | {dist:.1f}km")

        except Exception as e:
            print(f"Scraper error: {e}")

    # Send Telegram notifications for new unnotified listings
    for row in db.get_unnotified():
        notifier.send(row)
        db.mark_notified(row["url"])

    print("=== Done ===")


if __name__ == "__main__":
    db.init_db()
    run_scrapers()  # Run immediately on start

    schedule.every().hour.do(run_scrapers)
    print("Scheduler started — checking every hour.")
    while True:
        schedule.run_pending()
        time.sleep(60)
