from .db import get_conn
from .repository import create_fuar, create_user
from .security import hash_password

SEED_USERS = [
    ("Admin", "Örnek", "5550000001", "admin@backrows.local", "Admin123!", "admin"),
    ("Katilimci", "Örnek", "5550000002", "katilimci@backrows.local", "Katilimci123!", "katilimci"),
    ("Ziyaretci", "Örnek", "5550000003", "ziyaretci@backrows.local", "Ziyaretci123!", "ziyaretci"),
]

SEED_FUARLAR = [
    ("İstanbul Kitap Fuarı", "23/05/2026"),
    ("Ankara Cam Fuarı", "15/06/2026"),
    ("İzmir Bilim Fuarı", "10/06/2026"),
    ("Antalya Uçak Fuarı", "22/08/2026"),
    ("Kocaeli Araba Fuarı", "26/11/2026"),
]


def seed_if_empty() -> None:
    with get_conn() as conn:
        user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        fuar_count = conn.execute("SELECT COUNT(*) AS c FROM fuarlar").fetchone()["c"]

    if user_count == 0:
        for ad, soyad, telefon, eposta, sifre, rol in SEED_USERS:
            create_user(ad, soyad, telefon, eposta, hash_password(sifre), rol)

    if fuar_count == 0:
        for ad, tarih in SEED_FUARLAR:
            create_fuar(ad, tarih)
