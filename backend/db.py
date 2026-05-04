import sqlite3
import os
from contextlib import contextmanager
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "listings.db")


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                agency TEXT NOT NULL,
                title TEXT,
                location TEXT,
                price INTEGER,
                area REAL,
                distance_km REAL,
                interested INTEGER DEFAULT 0,
                notified INTEGER DEFAULT 0,
                found_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def is_known(url: str) -> bool:
    with _conn() as conn:
        row = conn.execute("SELECT 1 FROM listings WHERE url = ?", (url,)).fetchone()
        return row is not None


def insert(url: str, agency: str, title: str, location: str,
           price: Optional[int], area: Optional[float], distance_km: float):
    with _conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO listings (url, agency, title, location, price, area, distance_km)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (url, agency, title, location, price, area, distance_km))
        conn.commit()


def mark_notified(url: str):
    with _conn() as conn:
        conn.execute("UPDATE listings SET notified = 1 WHERE url = ?", (url,))
        conn.commit()


def set_interested(listing_id: int, value: bool):
    with _conn() as conn:
        conn.execute("UPDATE listings SET interested = ? WHERE id = ?", (int(value), listing_id))
        conn.commit()


def get_all(agency: Optional[str] = None) -> list[dict]:
    with _conn() as conn:
        if agency:
            rows = conn.execute(
                "SELECT * FROM listings WHERE agency = ? ORDER BY found_at DESC", (agency,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM listings ORDER BY found_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def get_unnotified() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM listings WHERE notified = 0 ORDER BY found_at ASC"
        ).fetchall()
        return [dict(r) for r in rows]
