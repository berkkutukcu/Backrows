import sqlite3
from typing import Optional

from .db import get_conn
from .security import create_qr_token


def get_user_by_email(eposta: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE eposta = ?", (eposta,)
        ).fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def get_user_by_qr_token(token: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE qr_token = ?", (token,)
        ).fetchone()


def create_user(
    ad: str,
    soyad: str,
    telefon: str,
    eposta: str,
    sifre_hash: str,
    rol: str,
) -> int:
    token = create_qr_token()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (ad, soyad, telefon, eposta, sifre_hash, rol, qr_token) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ad, soyad, telefon, eposta, sifre_hash, rol, token),
        )
        return cur.lastrowid


def delete_user(user_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


def list_users(rol: Optional[str] = None) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if rol:
            return conn.execute(
                "SELECT * FROM users WHERE rol = ? ORDER BY id", (rol,)
            ).fetchall()
        return conn.execute("SELECT * FROM users ORDER BY rol, id").fetchall()


def create_fuar(ad: str, tarih: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO fuarlar (ad, tarih) VALUES (?, ?)", (ad, tarih)
        )
        return cur.lastrowid


def list_fuarlar() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM fuarlar ORDER BY id").fetchall()


def get_fuar(fuar_id: int) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM fuarlar WHERE id = ?", (fuar_id,)
        ).fetchone()


def list_user_fuarlar(user_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT f.* FROM fuarlar f "
            "JOIN fuar_kayitlari fk ON fk.fuar_id = f.id "
            "WHERE fk.user_id = ? ORDER BY f.id",
            (user_id,),
        ).fetchall()


def join_fuar(user_id: int, fuar_id: int) -> bool:
    with get_conn() as conn:
        try:
            conn.execute(
                "INSERT INTO fuar_kayitlari (user_id, fuar_id) VALUES (?, ?)",
                (user_id, fuar_id),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def list_etkinlikler(
    fuar_id: Optional[int] = None, status: Optional[str] = None
) -> list[sqlite3.Row]:
    query = (
        "SELECT e.*, f.ad AS fuar_adi FROM etkinlikler e "
        "JOIN fuarlar f ON f.id = e.fuar_id"
    )
    clauses: list[str] = []
    params: list = []
    if fuar_id is not None:
        clauses.append("e.fuar_id = ?")
        params.append(fuar_id)
    if status is not None:
        clauses.append("e.status = ?")
        params.append(status)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY e.fuar_id, e.saat"
    with get_conn() as conn:
        return conn.execute(query, params).fetchall()


def create_etkinlik_request(
    fuar_id: int, saat: str, konusmaci: str, status: str = "bekliyor"
) -> Optional[int]:
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO etkinlikler (fuar_id, saat, konusmaci, status) "
                "VALUES (?, ?, ?, ?)",
                (fuar_id, saat, konusmaci, status),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None


def approve_etkinlik(etkinlik_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE etkinlikler SET status = 'onayli' WHERE id = ?",
            (etkinlik_id,),
        )


def save_verification(
    eposta: str,
    kod: str,
    ad: str,
    soyad: str,
    telefon: str,
    sifre_hash: str,
    expires_at: str,
) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO email_dogrulama "
            "(eposta, kod, ad, soyad, telefon, sifre_hash, expires_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (eposta, kod, ad, soyad, telefon, sifre_hash, expires_at),
        )


def get_verification(eposta: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM email_dogrulama WHERE eposta = ?", (eposta,)
        ).fetchone()


def delete_verification(eposta: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM email_dogrulama WHERE eposta = ?", (eposta,))
