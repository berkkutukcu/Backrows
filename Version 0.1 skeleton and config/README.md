# BackRows — Web Sürümü

Java Swing sürümünün FastAPI + Uvicorn + SQLite ile yeniden yazılmış hâli.

## Kurulum

```bash
cd WebSurum
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # SECRET_KEY değerini değiştir
```

## Çalıştırma

```bash
uvicorn app.main:app --reload
```

Tarayıcıda: http://localhost:8000

## Varsayılan Hesaplar (ilk çalıştırmada seed edilir)

| Rol | E-posta | Şifre |
|---|---|---|
| Admin | `admin@backrows.local` | `Admin123!` |
| Katılımcı | `katilimci@backrows.local` | `Katilimci123!` |
| Ziyaretçi | `ziyaretci@backrows.local` | `Ziyaretci123!` |

## Testler

```bash
pytest
```

## Klasör Yapısı

```
WebSurum/
├── app/            # FastAPI uygulaması
│   ├── routers/    # HTTP endpoint modülleri
│   ├── config.py   # Ayarlar
│   ├── db.py       # SQLite yardımcıları
│   ├── main.py     # Uygulama giriş noktası
│   ├── security.py # bcrypt + oturum
│   └── seed.py     # İlk kurulum verileri
├── templates/      # Jinja2 HTML şablonları
├── static/         # CSS, JS, resimler
├── data/           # SQLite veritabanı + yüklenen dosyalar
└── tests/          # pytest testleri
```
