def test_login_success(client):
    r = client.post(
        "/login",
        data={"eposta": "admin@backrows.local", "sifre": "Admin123!"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/admin"


def test_login_wrong_password(client):
    r = client.post(
        "/login",
        data={"eposta": "admin@backrows.local", "sifre": "yanlis!1234"},
    )
    assert r.status_code == 401
    assert "E-posta veya şifre hatalı" in r.text


def test_login_unknown_email(client):
    r = client.post(
        "/login",
        data={"eposta": "yok@backrows.local", "sifre": "whatever1!"},
    )
    assert r.status_code == 401


def test_protected_routes_redirect_when_unauth(client):
    r = client.get("/admin", follow_redirects=False)
    # require_admin raises 403 for non-admin; 401 redirect for missing session.
    assert r.status_code in (401, 303)


def test_admin_cannot_access_katilimci_panel(admin_client):
    r = admin_client.get("/katilimci", follow_redirects=False)
    assert r.status_code == 403


def test_logout_clears_session(admin_client):
    admin_client.get("/logout", follow_redirects=False)
    r = admin_client.get("/admin", follow_redirects=False)
    assert r.status_code != 200


def test_register_then_verify_then_login(client):
    r = client.post(
        "/register",
        data={
            "ad": "Yeni",
            "soyad": "Ziyaretci",
            "telefon": "5551112233",
            "eposta": "yeni.ziyaretci@example.com",
            "sifre": "Pass1234!",
            "sifre_tekrar": "Pass1234!",
        },
    )
    assert r.status_code == 200
    # The 4-digit verification code is shown on the page (Java parity).
    import re

    m = re.search(r"<strong[^>]*>(\d{4})</strong>", r.text)
    assert m, "verification code not displayed"
    kod = m.group(1)

    r = client.post(
        "/register/verify",
        data={"eposta": "yeni.ziyaretci@example.com", "kod": kod},
    )
    assert r.status_code == 200
    assert "Kayıt tamamlandı" in r.text

    r = client.post(
        "/login",
        data={"eposta": "yeni.ziyaretci@example.com", "sifre": "Pass1234!"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/ziyaretci"


def test_register_validation_errors(client):
    r = client.post(
        "/register",
        data={
            "ad": "A",  # too short
            "soyad": "Test",
            "telefon": "0551234567",  # leading zero
            "eposta": "geçersiz",
            "sifre": "kısa",
            "sifre_tekrar": "kısa",
        },
    )
    assert r.status_code == 400
    assert "harf" in r.text or "Ad" in r.text


def test_register_duplicate_email(client):
    r = client.post(
        "/register",
        data={
            "ad": "Tekrar",
            "soyad": "Eden",
            "telefon": "5551112299",
            "eposta": "admin@backrows.local",  # already seeded
            "sifre": "Pass1234!",
            "sifre_tekrar": "Pass1234!",
        },
    )
    assert r.status_code == 400
    assert "zaten kayıtlı" in r.text


def test_qr_login_flow(client):
    # Get admin's QR token from the admin/qr page
    client.post(
        "/login",
        data={"eposta": "admin@backrows.local", "sifre": "Admin123!"},
        follow_redirects=False,
    )
    r = client.get("/admin/qr")
    import re

    m = re.search(r"<code>([^<]+)</code>", r.text)
    assert m
    token = m.group(1)
    client.get("/logout", follow_redirects=False)

    # POST /qr-login with that token
    r = client.post("/qr-login", json={"token": token})
    assert r.status_code == 200
    assert r.json()["redirect"] == "/admin"


def test_qr_login_bad_token(client):
    r = client.post("/qr-login", json={"token": "geçersiz-token-zzz"})
    assert r.status_code == 401
