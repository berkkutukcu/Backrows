import re

AD_SOYAD_RE = re.compile(r"^[a-zA-ZçÇğĞıİöÖşŞüÜ]{2,}$")
TELEFON_RE = re.compile(r"^[1-9]\d{9}$")
EPOSTA_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
TARIH_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
SAAT_RE = re.compile(r"^([01]\d|2[0-2])\.[0-5]\d$")

MIN_SIFRE_UZUNLUK = 8
OZEL_KARAKTER_RE = re.compile(r"[^a-zA-Z0-9]")


def ad_soyad_gecerli(deger: str) -> bool:
    return bool(AD_SOYAD_RE.match(deger))


def telefon_gecerli(deger: str) -> bool:
    return bool(TELEFON_RE.match(deger))


def eposta_gecerli(deger: str) -> bool:
    return bool(EPOSTA_RE.match(deger))


def sifre_gecerli(deger: str) -> bool:
    return len(deger) >= MIN_SIFRE_UZUNLUK and bool(OZEL_KARAKTER_RE.search(deger))


def tarih_gecerli(deger: str) -> bool:
    m = TARIH_RE.match(deger)
    if not m:
        return False
    gun, ay, yil = (int(x) for x in m.groups())
    return 1 <= gun <= 31 and 1 <= ay <= 12 and yil >= 2024


def saat_gecerli(deger: str) -> bool:
    if not SAAT_RE.match(deger):
        return False
    saat = int(deger.split(".")[0])
    return 9 <= saat <= 22
