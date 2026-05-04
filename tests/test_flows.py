def test_admin_creates_fair(admin_client):
    r = admin_client.post(
        "/admin/fairs",
        data={"ad": "Test Fuarı", "tarih": "15/07/2026"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = admin_client.get("/admin/fairs")
    assert "Test Fuarı" in r.text


def test_admin_rejects_invalid_date(admin_client):
    r = admin_client.post(
        "/admin/fairs",
        data={"ad": "Bozuk", "tarih": "31-12-2030"},
    )
    assert r.status_code == 400
    assert "GG/AA/YYYY" in r.text


def test_katilimci_join_and_request(katilimci_client, client):
    # join fair 1
    r = katilimci_client.post("/katilimci/fairs/1/join", follow_redirects=False)
    assert r.status_code == 303
    assert "mesaj=" in r.headers["location"]
    # duplicate join
    r = katilimci_client.post("/katilimci/fairs/1/join", follow_redirects=False)
    assert r.status_code == 303
    assert "hata=" in r.headers["location"]
    # event request
    r = katilimci_client.post(
        "/katilimci/event-request",
        data={"fuar_id": 1, "saat": "14.00"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "mesaj=" in r.headers["location"]
    # duplicate slot
    r = katilimci_client.post(
        "/katilimci/event-request",
        data={"fuar_id": 1, "saat": "14.00"},
        follow_redirects=False,
    )
    assert "hata=Bu+saat+dolu" in r.headers["location"]
    # request for unjoined fair
    r = katilimci_client.post(
        "/katilimci/event-request",
        data={"fuar_id": 2, "saat": "10.00"},
        follow_redirects=False,
    )
    assert "kat%C4%B1lmal" in r.headers["location"]


def test_full_workflow_request_approve_visible(client):
    # 1. Katilimci joins fair 1 and creates event request
    client.post(
        "/login",
        data={"eposta": "katilimci@backrows.local", "sifre": "Katilimci123!"},
        follow_redirects=False,
    )
    client.post("/katilimci/fairs/1/join", follow_redirects=False)
    client.post(
        "/katilimci/event-request",
        data={"fuar_id": 1, "saat": "16.00"},
        follow_redirects=False,
    )
    client.get("/logout", follow_redirects=False)

    # 2. Admin sees pending event and approves it
    client.post(
        "/login",
        data={"eposta": "admin@backrows.local", "sifre": "Admin123!"},
        follow_redirects=False,
    )
    r = client.get("/admin/events")
    assert "Bekleyen" in r.text and "16.00" in r.text
    import re

    m = re.search(r"/admin/events/(\d+)/approve", r.text)
    assert m
    eid = m.group(1)
    client.post(f"/admin/events/{eid}/approve", follow_redirects=False)
    client.get("/logout", follow_redirects=False)

    # 3. Ziyaretci joins fair 1 and views events
    client.post(
        "/login",
        data={"eposta": "ziyaretci@backrows.local", "sifre": "Ziyaretci123!"},
        follow_redirects=False,
    )
    client.post("/ziyaretci/fairs/1/join", follow_redirects=False)
    r = client.get("/ziyaretci/events?fuar_id=1")
    assert "16.00" in r.text


def test_admin_creates_user_and_can_delete(admin_client):
    r = admin_client.post(
        "/admin/users",
        data={
            "ad": "Test",
            "soyad": "Kullanici",
            "telefon": "5559998877",
            "eposta": "test.user@example.com",
            "sifre": "Pass1234!",
            "rol": "katilimci",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = admin_client.get("/admin/users")
    assert "test.user@example.com" in r.text
    # delete the new user (find ID)
    import re

    m = re.search(
        r"<tr>\s*<td>(\d+)</td>\s*<td>Test Kullanici</td>", r.text
    )
    assert m
    uid = m.group(1)
    r = admin_client.post(f"/admin/users/{uid}/delete", follow_redirects=False)
    assert r.status_code == 303
    r = admin_client.get("/admin/users")
    assert "test.user@example.com" not in r.text


def test_admin_self_delete_blocked(admin_client):
    # Find current admin's id
    r = admin_client.get("/admin/users")
    import re

    m = re.search(r"<tr>\s*<td>(\d+)</td>\s*<td>[^<]*</td>\s*<td>admin@backrows.local", r.text)
    assert m
    admin_id = m.group(1)
    r = admin_client.post(f"/admin/users/{admin_id}/delete", follow_redirects=False)
    assert r.status_code == 303
    assert "hata=" in r.headers["location"]
    r = admin_client.get("/admin/users")
    assert "admin@backrows.local" in r.text


def test_qr_image_returns_png(admin_client):
    r = admin_client.get("/admin/qr")
    import re

    m = re.search(r"<code>([^<]+)</code>", r.text)
    assert m
    token = m.group(1)
    r = admin_client.get(f"/qr/{token}.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_qr_image_unknown_token_404(client):
    r = client.get("/qr/yokboyle-token-zzz.png")
    assert r.status_code == 404
