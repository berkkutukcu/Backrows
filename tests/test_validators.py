import pytest

from app.validators import (
    ad_soyad_gecerli,
    eposta_gecerli,
    saat_gecerli,
    sifre_gecerli,
    tarih_gecerli,
    telefon_gecerli,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Berk", True),
        ("Şükriye", True),
        ("İbrahim", True),
        ("ÇiğdemÖzgürŞule", True),
        ("A", False),  # too short
        ("", False),
        ("Ali2", False),  # digit
        ("Ali Veli", False),  # space
        ("Ali-Veli", False),  # dash
    ],
)
def test_ad_soyad(value, expected):
    assert ad_soyad_gecerli(value) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("5551234567", True),
        ("1234567890", True),
        ("0551234567", False),  # leading 0
        ("555123456", False),  # 9 digits
        ("55512345678", False),  # 11 digits
        ("555 123 4567", False),  # spaces
        ("", False),
    ],
)
def test_telefon(value, expected):
    assert telefon_gecerli(value) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("ali@example.com", True),
        ("admin@backrows.local", True),
        ("ali.example.com", False),  # no @
        ("ali@example", False),  # no .
        ("aliexamplecom", False),
        ("", False),
    ],
)
def test_eposta(value, expected):
    assert eposta_gecerli(value) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Admin123!", True),
        ("abcdefg!", True),
        ("Pass1*ord", True),
        ("abcdefgh", False),  # no special char
        ("Aa1!", False),  # too short
        ("", False),
    ],
)
def test_sifre(value, expected):
    assert sifre_gecerli(value) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("15/07/2026", True),
        ("01/01/2024", True),
        ("31/12/2099", True),
        ("15/13/2026", False),  # ay 13
        ("32/05/2026", False),  # gün 32
        ("00/05/2026", False),  # gün 0
        ("15/05/2023", False),  # yıl < 2024
        ("15-07-2026", False),  # dash
        ("2026/07/15", False),  # wrong order
        ("", False),
    ],
)
def test_tarih(value, expected):
    assert tarih_gecerli(value) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("09.00", True),
        ("22.00", True),
        ("14.30", True),
        ("08.00", False),  # before 09
        ("23.00", False),  # after 22
        ("14:30", False),  # colon, not dot
        ("9.00", False),  # missing leading zero
        ("", False),
    ],
)
def test_saat(value, expected):
    assert saat_gecerli(value) is expected
