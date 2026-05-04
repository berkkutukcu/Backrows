import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ad          TEXT NOT NULL,
    soyad       TEXT NOT NULL,
    telefon     TEXT NOT NULL,
    eposta      TEXT NOT NULL UNIQUE,
    sifre_hash  TEXT NOT NULL,
    rol         TEXT NOT NULL CHECK(rol IN ('admin','katilimci','ziyaretci')),
    qr_token    TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS fuarlar (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ad      TEXT NOT NULL,
    tarih   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fuar_kayitlari (
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fuar_id  INTEGER NOT NULL REFERENCES fuarlar(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, fuar_id)
);

CREATE TABLE IF NOT EXISTS etkinlikler (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fuar_id     INTEGER NOT NULL REFERENCES fuarlar(id) ON DELETE CASCADE,
    saat        TEXT NOT NULL,
    konusmaci   TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'onayli' CHECK(status IN ('onayli','bekliyor')),
    UNIQUE(fuar_id, saat)
);

CREATE TABLE IF NOT EXISTS email_dogrulama (
    eposta      TEXT PRIMARY KEY,
    kod         TEXT NOT NULL,
    ad          TEXT NOT NULL,
    soyad       TEXT NOT NULL,
    telefon     TEXT NOT NULL,
    sifre_hash  TEXT NOT NULL,
    expires_at  TEXT NOT NULL
);
"""


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)
