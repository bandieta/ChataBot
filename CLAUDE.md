# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A real estate monitoring bot for the Katowice area. Scrapes ~24 Polish real estate agency websites hourly, filters listings (house for sale, 100–180 m², within 15 km of Katowice), sends Telegram notifications for new matches, and serves a NextJS dashboard.

## Running

```bash
# All-in-one (installs deps, starts API + scraper + frontend)
./run.sh

# Or separately:
cd backend && pip install -r requirements.txt
uvicorn api:app --port 8000          # REST API
python main.py                        # hourly scraper + Telegram notifier
cd frontend && npm install && npm run dev   # NextJS on port 3000
```

## Architecture

```
backend/
  main.py        — scheduler (runs every hour), filters listings, sends Telegram
  api.py         — FastAPI on port 8000 (read listings, toggle interest)
  db.py          — SQLite helpers (listings.db)
  geocoder.py    — haversine distance + pre-cached Silesian cities + Nominatim fallback
  notifier.py    — Telegram Bot API (token hardcoded, chat_id = 7760838175)
  scrapers/
    base.py      — Listing dataclass
    ire.py       — IRE/OpenRem platform (Łowcy Nieruchomości, SCN) — area in URL slug
    rema.py      — REMA (WordPress)
    realton.py   — Realton (WordPress)
    truhome.py   — TRUhome
    indexo.py    — Indexo (PHP)
    wgn.py       — WGN Katowice
    kopalnia.py  — Kopalnia Nieruchomości
frontend/
  app/page.tsx   — listings table, agency filter, interested checkbox
  next.config.ts — proxies /api/* → localhost:8000
```

## Adding a new agency scraper

1. Create `backend/scrapers/myscraper.py` with a `scrape() -> list[Listing]` function
2. Import and add to `get_all_scrapers()` in `backend/scrapers/__init__.py`

## Key constants

- Filter: area 100–180 m², distance ≤ 15 km from Katowice (50.2649, 19.0238)
- Telegram token: in `notifier.py` (also reads `TELEGRAM_TOKEN` env var)
- DB: `backend/listings.db` (auto-created on first run)

## IRE platform pattern

Agencies on the IRE/OpenRem platform (Łowcy, SCN) encode area and price in the listing URL slug:
`domy-na-sprzedaz-{price}zl-{area}m2-{city}-{district}-o{id}`
No need to fetch detail pages — filter by area from URL alone.
