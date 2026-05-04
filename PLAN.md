# BackRows — Java Swing'den FastAPI + SQLite Web Sürümüne Taşıma Planı

## Bağlam

`JavaProject/` dizininde bulunan **BackRows Etkinlik ve Fuar Yönetim Sistemi**, Java Swing ile yazılmış bir masaüstü uygulaması. Üç kullanıcı tipi (Admin, Katılımcı, Ziyaretçi), fuar kayıtları, etkinlik onay süreci ve QR ile giriş özelliklerini içeriyor. Veriler CSV formatında düz metin dosyalarında saklanıyor; dosya yolları geliştiricinin kullanıcı adına gömülü; şifreler metadata hash'iyle tutulmakla birlikte login kontrolü düz metinle yapılıyor.

**Amaç**: Aynı iş mantığını ve Türkçe terminolojiyi koruyarak, uygulamayı **FastAPI + Uvicorn + SQLite** tabanlı bir web uygulamasına dönüştürmek. Yeni proje `WebSurum/` klasörüne oluşturulacak; Java projesi olduğu gibi bırakılacak (referans).

**Faydalar**: Taşınabilirlik (hardcoded path yok), gerçek kimlik doğrulama (bcrypt), tarayıcıdan çok platformlu erişim, tek bir SQLite dosyasında tutarlı veri.

---

## Teknoloji Seçimleri

| Alan | Seçim | Gerekçe |
|---|---|---|
| Web framework | **FastAPI** | Modern, async, otomatik OpenAPI, Pydantic validation |
| ASGI sunucu | **Uvicorn** | Kullanıcının isteği |
| Veritabanı | **SQLite** (stdlib `sqlite3` modülü) | Kullanıcının isteği; harici bağımlılık yok |
| ORM | **Yok** (düz SQL + yardımcı fonksiyonlar) | Küçük uygulama; bağımlılığı minimumda tutmak için |
| Şablon motoru | **Jinja2** | FastAPI ile entegre, HTML sayfalar için |
| Statik dosyalar | `fastapi.staticfiles` | CSS/JS/resimler için |
| Form doğrulama | Pydantic + HTML5 + sunucu tarafı regex | Java tarafındaki regex'leri birebir koru |
| Oturum yönetimi | `itsdangerous` imzalı cookie (Starlette `SessionMiddleware`) | Basit, sunucu tarafı state yok |
| Şifre hash | **bcrypt** (`passlib[bcrypt]`) | Java'daki düz SHA-256'yı yükselt |
| QR kod | `qrcode[pil]` (üretim) + `html5-qrcode` JS kütüphanesi (tarayıcı kamerasından okuma) | `webcam-capture` + ZXing yerine; tarayıcı MediaDevices API ile çalışır |
| CSS | Basit custom CSS (yeşil temalı, Swing görünümüne yakın) | Ağır framework gerektirmiyor |

---

## Hedef Proje Yapısı (`WebSurum/`)

```
WebSurum/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, middleware, router kayıtları
│   ├── config.py                # Ayarlar: DB yolu, SECRET_KEY, upload klasörü
│   ├── db.py                    # SQLite bağlantı yardımcıları, init_db()
│   ├── security.py              # bcrypt hash/verify, oturum helper'ları
│   ├── dependencies.py          # current_user, require_role dependency'leri
│   ├── validators.py            # Türkçe regex'ler (telefon, ad, e-posta, şifre)
│   ├── routers/
│   │   ├── auth.py              # /login, /logout, /register, /qr-login, /register/verify
│   │   ├── admin.py             # /admin/* (dashboard, kullanıcı/fuar/etkinlik yönetimi)
│   │   ├── katilimci.py         # /katilimci/* (fuar kayıt, QR göster, etkinlik talep)
│   │   ├── ziyaretci.py         # /ziyaretci/* (fuar kayıt, QR göster, etkinlikler)
│   │   └── qr.py                # /qr/{user_id}.png — QR görüntü üretimi
│   ├── schemas.py               # Pydantic modelleri (LoginRequest, RegisterRequest, ...)
│   ├── repository.py            # Kullanıcı/fuar/etkinlik CRUD SQL fonksiyonları
│   └── seed.py                  # İlk çalıştırmada Java CSV verilerini SQLite'a aktar
├── templates/
│   ├── base.html                # Ortak layout (header, footer, stil)
│   ├── login.html               # /login — e-posta+şifre + QR butonu + slideshow
│   ├── register.html            # /register — kayıt formu
│   ├── verify_email.html        # 4 haneli kod doğrulama
│   ├── qr_login.html            # Tarayıcı kamera ile QR tarama
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html           # Kullanıcı ekle/listele/sil
│   │   ├── fairs.html           # Yeni fuar oluştur + listele
│   │   ├── events_approval.html # Bekleyen etkinlikler (// öneki olanlar)
│   │   ├── announcements.html   # 5 slot halinde duyuru resimleri
│   │   └── qr.html              # Admin'in kendi QR'ı
│   ├── katilimci/
│   │   ├── dashboard.html
│   │   ├── fairs.html           # Tüm fuarlar + katıldığım fuarlar
│   │   ├── event_request.html   # Etkinlik isteği oluştur
│   │   └── qr.html
│   └── ziyaretci/
│       ├── dashboard.html
│       ├── fairs.html
│       ├── events.html          # Etkinlikleri listele
│       └── qr.html
├── static/
│   ├── css/style.css            # Yeşil temalı stil
│   ├── js/
│   │   ├── qr-scanner.js        # html5-qrcode wrapper
│   │   └── slideshow.js         # Login sayfasında carousel
│   └── images/                  # backrowslogo.png, backrowsicon.png, DuyuruFoto1-5.png
├── data/
│   ├── backrows.db              # SQLite veritabanı (ilk çalıştırmada oluşturulur)
│   └── uploads/
│       └── announcements/       # DuyuruFoto1-5.png yüklenen dosyalar
├── tests/
│   ├── test_auth.py             # Login, register, şifre doğrulama testleri
│   ├── test_validators.py       # Türkçe regex testleri
│   └── test_flows.py            # Fuar kayıt, etkinlik onay akışları
├── requirements.txt
├── .env.example                 # SECRET_KEY örneği
├── .gitignore
└── README.md                    # Kurulum ve çalıştırma talimatları
```

---

## SQLite Şeması (`app/db.py` içinde `init_db()`)

CSV dosyalarını yapılandırılmış tablolarla değiştiriyoruz. Mevcut `etkinlikler` CSV'sinde `//` öneki "bekliyor" anlamına geliyordu; bunu `status` sütunuyla temsil edeceğiz.

```sql
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ad          TEXT NOT NULL,
    soyad       TEXT NOT NULL,
    telefon     TEXT NOT NULL,
    eposta      TEXT NOT NULL UNIQUE,
    sifre_hash  TEXT NOT NULL,           -- bcrypt
    rol         TEXT NOT NULL CHECK(rol IN ('admin','katilimci','ziyaretci')),
    qr_token    TEXT NOT NULL UNIQUE,    -- QR içeriğinde kullanıcı ID yerine opak token
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE fuarlar (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ad      TEXT NOT NULL,
    tarih   TEXT NOT NULL                -- "GG/AA/YYYY" formatı korunuyor
);

CREATE TABLE fuar_kayitlari (             -- Kullanıcı <-> Fuar katılım
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fuar_id  INTEGER NOT NULL REFERENCES fuarlar(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, fuar_id)
);

CREATE TABLE etkinlikler (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fuar_id     INTEGER NOT NULL REFERENCES fuarlar(id) ON DELETE CASCADE,
    saat        TEXT NOT NULL,           -- "HH.MM" formatı
    konusmaci   TEXT NOT NULL,           -- katılımcı adı veya firma
    status      TEXT NOT NULL DEFAULT 'onayli' CHECK(status IN ('onayli','bekliyor')),
    UNIQUE(fuar_id, saat)
);

CREATE TABLE email_dogrulama (            -- Kayıt sırasında geçici 4 haneli kod
    eposta      TEXT PRIMARY KEY,
    kod         TEXT NOT NULL,
    ad          TEXT NOT NULL,
    soyad       TEXT NOT NULL,
    telefon     TEXT NOT NULL,
    sifre_hash  TEXT NOT NULL,
    expires_at  TEXT NOT NULL
);
```

Java sürümünde üç ayrı dosya (Adminler/Katilimcilar/Ziyaretciler) vardı; tek `users` tablosu + `rol` kolonu çok daha temiz. Giriş akışında üç dosyayı sırayla arama mantığı (`checkUserCredentials`) tek sorguya düşüyor.

---

## Uygulama Fazları (Adım Adım)

### Faz 0 — İskelet ve Kurulum
1. `WebSurum/` içinde klasör yapısını oluştur.
2. `requirements.txt` yaz: `fastapi`, `uvicorn[standard]`, `jinja2`, `python-multipart`, `passlib[bcrypt]`, `itsdangerous`, `qrcode[pil]`, `pydantic`, `pytest`.
3. `.env.example` ve `.gitignore` yaz (`data/*.db`, `data/uploads/` dahil).
4. `README.md`: kurulum (`python -m venv .venv`, `pip install -r requirements.txt`), çalıştırma (`uvicorn app.main:app --reload`), varsayılan admin bilgisi.
5. `app/config.py`: `DB_PATH`, `UPLOAD_DIR`, `SECRET_KEY` (env'den oku, fallback dev değeri).
6. `app/db.py`: `get_conn()` bağlam yöneticisi (`row_factory = sqlite3.Row`, foreign keys açık), `init_db()` şemayı oluştur.
7. `app/main.py`: FastAPI instance, `SessionMiddleware`, static mount, template, router'lar (placeholder), startup event → `init_db()` + `seed_if_empty()`.

**Doğrulama**: `uvicorn app.main:app --reload` ile sunucu kalksın; `http://localhost:8000/` "Hoş geldiniz" gösterirsin.

### Faz 1 — Veritabanı + Seed
1. `app/seed.py`: İlk çalıştırmada `users` tablosu boşsa her rol için birer örnek hesap aç:
   - `admin@backrows.local` / `Admin123!` (rol=`admin`)
   - `katilimci@backrows.local` / `Katilimci123!` (rol=`katilimci`)
   - `ziyaretci@backrows.local` / `Ziyaretci123!` (rol=`ziyaretci`)
2. `fuarlar` tablosu boşsa gösterim amaçlı 3-5 örnek fuar ekle (ad + GG/AA/YYYY).
3. Eski CSV dosyalarından veri **aktarılmayacak** — kullanıcı tercihi.
4. `app/repository.py`: `get_user_by_email`, `get_user_by_qr_token`, `create_user`, `list_fuarlar`, `list_user_fuarlar`, `join_fuar`, `list_etkinlikler`, `create_etkinlik_request`, `approve_etkinlik` fonksiyonları.

**Doğrulama**: `sqlite3 data/backrows.db ".tables"` 5 tablo göstermeli; `SELECT eposta, rol FROM users` üç örnek hesabı dönmeli.

### Faz 2 — Kimlik Doğrulama ve Kayıt
1. `app/security.py`: `hash_password`, `verify_password`, `create_qr_token` (secrets.token_urlsafe).
2. `app/validators.py`: Java tarafındaki regex'leri birebir kopyala.
   - Ad/Soyad: `^[a-zA-ZçÇğĞıİöÖşŞüÜ]{2,}$`
   - Telefon: `^[1-9]\d{9}$` (10 hane, başında 0 yok)
   - E-posta: `@` ve `.` içermeli
   - Şifre: ≥ 8 karakter + en az bir özel karakter
   - Tarih: `^\d{2}/\d{2}/\d{4}$`, yıl ≥ 2024, gün 1-31, ay 1-12
3. `app/schemas.py`: `LoginIn`, `RegisterIn`, `FuarIn`, `EtkinlikRequestIn` Pydantic modelleri (validator'lar burada).
4. `app/routers/auth.py`:
   - `GET /` → `login.html` (slideshow: `static/images/DuyuruFoto1-5.png`)
   - `POST /login` → şifre doğrula, `request.session['user_id']` ve `['rol']` koy, role göre yönlendir
   - `GET /logout` → session clear
   - `GET /register` → `register.html`
   - `POST /register` → validate, `email_dogrulama`'ya 4 haneli kod yaz, `verify_email.html`'e yönlendir (kod ekranda görünür — Java'daki davranışın aynısı)
   - `POST /register/verify` → kod eşleşirse `users` tablosuna `rol='ziyaretci'` ile ekle, `qr_token` üret, login sayfasına yönlendir
   - `GET /qr-login` → `qr_login.html` (tarayıcı kamerası)
   - `POST /qr-login` → JSON body `{"token": "..."}` → `qr_token`'la kullanıcı bul, oturum aç, redirect URL dön
5. `app/dependencies.py`: `current_user(request)`, `require_admin`, `require_katilimci`, `require_ziyaretci`.

**Doğrulama**: Seed admin'iyle login; kayıt formunu doldurup yeni ziyaretçi oluştur; logout/login tekrarla.

### Faz 3 — Admin Paneli
Java `Adminler.java`'nın beş alt paneline karşılık:

1. `GET /admin` — dashboard (linkler).
2. `GET/POST /admin/users` — kullanıcı listele (role göre filtre), ekle, sil. Form: ad/soyad/telefon/eposta/şifre/rol.
3. `GET/POST /admin/fairs` — fuar listele + yeni fuar oluştur (ad + GG/AA/YYYY).
4. `GET /admin/events` — `status='bekliyor'` etkinlikler tablo halinde; her satırda `POST /admin/events/{id}/approve`. Onayla → `status='onayli'`.
5. `GET/POST /admin/announcements` — 5 slot (`DuyuruFoto1.png` … `DuyuruFoto5.png`). `UploadFile` ile al, PIL ile 400×400 PNG doğrula, `data/uploads/announcements/` altına yaz. Login slideshow'u buradan okur.
6. `GET /admin/qr` — oturumdaki admin'in `qr_token`'ını `/qr/{token}.png` üzerinden göster.

**Doğrulama**: Admin olarak giriş → yeni fuar ekle → çıkış → ziyaretçi olarak gir → yeni fuarı "Tüm Fuarlar"da gör.

### Faz 4 — Katılımcı Paneli
Java `Katilimcilar.java` karşılığı:

1. `GET /katilimci` — dashboard.
2. `GET /katilimci/fairs` — iki tablo: tüm fuarlar (Katıl butonu) + katıldığım fuarlar. `POST /katilimci/fairs/{id}/join` → `fuar_kayitlari`'na insert (tekrar engelle).
3. `GET/POST /katilimci/event-request` — ComboBox yerine `<select>`: sadece katıldığı fuarlar + saat (09.00-22.00). Submit → `etkinlikler` tablosuna `status='bekliyor'`, `konusmaci='<ad> <soyad>'` insert. Aynı `(fuar_id, saat)` varsa "saat dolu" hatası dön.
4. `GET /katilimci/qr` — QR göster.

### Faz 5 — Ziyaretçi Paneli
Java `Ziyaretciler.java` karşılığı (animasyonlar hariç; web'de hover CSS ile yapılır):

1. `GET /ziyaretci` — dashboard.
2. `GET /ziyaretci/fairs` — aynı katılımcı gibi (katıl/katıldıklarım).
3. `GET /ziyaretci/events?fuar_id=...` — seçilen fuarın `status='onayli'` etkinliklerini tablo halinde göster (saat, konuşmacı).
4. `GET /ziyaretci/qr` — QR göster.

### Faz 6 — QR Servisi
1. `GET /qr/{token}.png` — `qrcode` kütüphanesi ile token'ı PNG'ye çevir, `StreamingResponse` ile dön.
2. `templates/qr_login.html` + `static/js/qr-scanner.js` — `html5-qrcode` kütüphanesi CDN'den, `onScanSuccess(token)` → `fetch('/qr-login', {token})` → JSON `{redirect: "/admin"}` → `window.location`.

**Doğrulama**: Telefonla `/admin/qr` sayfasındaki QR'ı çek; masaüstüde `/qr-login`'da web kamerasıyla QR'ı oku → otomatik giriş.

### Faz 7 — UI İnce Ayar ve Türkçe Terimler
1. `base.html`: yeşil header (Java'daki renk kodlarını eşle — RGB değerlerini kaynak Swing dosyalarından çekeceğim implementasyonda), Türkçe menü (Giriş Yap / Kayıt Ol / Fuarlar / Etkinlikler / QR Göster / Çıkış).
2. Tüm form etiketleri, hata mesajları, tablo başlıkları Türkçe. Hata metinleri Java `JOptionPane` mesajlarından kopyalanacak ("E-posta veya şifre hatalı", "Bu fuara zaten katıldınız", vb.).
3. Login slideshow JS: her 5 saniyede bir görselleri döndür, radio butonlarla manuel seçim (Java davranışı).
4. Easter egg özelliği **yapılmayacak** — kullanıcı tercihi. `Easteregg.java`, `tanerhoca100` tetikleyicisi ve `frame_00-71.jpg` dosyaları Python sürümüne taşınmayacak.

### Faz 8 — Testler
1. `tests/test_validators.py`: telefon/ad/e-posta/şifre/tarih regex'leri için geçerli ve geçersiz case'ler.
2. `tests/test_auth.py`: `TestClient` ile register → verify → login → logout → QR login akışı.
3. `tests/test_flows.py`: admin fuar oluştur, katılımcı kayıt ol + katıl + etkinlik iste, admin onayla, ziyaretçi listede gör.

**Doğrulama**: `pytest` yeşil.

### Faz 9 — Belgeler ve Son Temizlik
1. `README.md`: Kurulum, seed edilen admin bilgisi, `uvicorn app.main:app --reload` komutu, test nasıl çalıştırılır, klasör yapısı özeti.
2. `.env.example` içinde `SECRET_KEY=<değiştir-beni>` ve `DB_PATH=./data/backrows.db`.
3. `app/config.py` yolları göreli tut (hardcoded kullanıcı adı yok — Java'nın hatasını tekrarlama).

---

## Kritik Dosyalar (Referans için Java tarafı)

| İşlev | Java | Yeni Python karşılığı |
|---|---|---|
| Giriş kontrolü | [Login.java](JavaProject/src/Login.java) `checkUserCredentials()` | [app/routers/auth.py](WebSurum/app/routers/auth.py) `login()` |
| Kayıt | [Register.java](JavaProject/src/Register.java) + [Epostaonay.java](JavaProject/src/Epostaonay.java) | [app/routers/auth.py](WebSurum/app/routers/auth.py) `register()` + `verify()` |
| Dosya yolu sabitleri | [DosyaYollari.java](JavaProject/src/DosyaYollari.java) | [app/config.py](WebSurum/app/config.py) |
| Admin panel | [Adminler.java](JavaProject/src/Adminler.java) | [app/routers/admin.py](WebSurum/app/routers/admin.py) |
| Katılımcı | [Katilimcilar.java](JavaProject/src/Katilimcilar.java) | [app/routers/katilimci.py](WebSurum/app/routers/katilimci.py) |
| Ziyaretçi | [Ziyaretciler.java](JavaProject/src/Ziyaretciler.java) | [app/routers/ziyaretci.py](WebSurum/app/routers/ziyaretci.py) |
| QR okuma | [Qrcam.java](JavaProject/src/Qrcam.java) (webcam-capture + ZXing) | `templates/qr_login.html` + `static/js/qr-scanner.js` (html5-qrcode tarayıcıda) |
| User model | [User.java](JavaProject/src/User.java) + [Ziyaretci.java](JavaProject/src/Ziyaretci.java) | `users` tablosu + `fuar_kayitlari` |

---

## Kullanıcı Tercihleri (Onaylandı)

- **Veri aktarımı**: CSV'den aktarım yok. Üç rol için birer örnek hesap + örnek fuarlar seed edilecek.
- **QR giriş**: Tarayıcı kamerası (`html5-qrcode`).
- **E-posta doğrulama**: Java gibi 4 haneli kod sayfada gösterilecek. SMTP yok.
- **Easter egg**: Yapılmayacak.

---

## Uçtan Uca Doğrulama Kontrol Listesi

Uygulama tamamlandığında aşağıdaki akışların tümü çalışmalı:

- [ ] `uvicorn app.main:app --reload` hatasız kalkıyor, `http://localhost:8000/` login sayfasını döndürüyor.
- [ ] Üç seed hesabının her biriyle (`admin@/katilimci@/ziyaretci@backrows.local`) giriş → ilgili dashboard açılıyor.
- [ ] `/register` → 4 haneli kod → yeni ziyaretçi oluştur → yeni hesapla giriş yap.
- [ ] Admin yeni fuar oluştursun, yeni katılımcı ekleyebilsin.
- [ ] Katılımcı fuara katılsın, etkinlik isteği oluştursun.
- [ ] Admin bekleyen etkinliği onaylasın.
- [ ] Ziyaretçi aynı fuarın etkinliklerini listede görsün.
- [ ] QR göster → telefon/ikinci cihazda `/qr-login` ile giriş yap.
- [ ] Admin 400×400 PNG duyuru yükle → login sayfasında slideshow'da görünsün.
- [ ] `pytest` tüm testleri geçsin.
- [ ] `data/backrows.db` dışında yazılan herhangi bir kalıcı veri olmamalı (CSV yok).
- [ ] Kod tabanında tek bir hardcoded kullanıcı yolu (`C:\Users\...`) bulunmamalı.
