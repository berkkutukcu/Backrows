import os
import tempfile
from pathlib import Path

# Set isolated paths BEFORE any app module imports.
_TMP = Path(tempfile.mkdtemp(prefix="backrows-test-"))
os.environ["DB_PATH"] = str(_TMP / "test.db")
os.environ["UPLOAD_DIR"] = str(_TMP / "uploads")
os.environ["SECRET_KEY"] = "test-secret"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed_if_empty  # noqa: E402


@pytest.fixture
def fresh_db():
    """Wipe and re-seed the test DB for tests that need a clean slate."""
    db_path = Path(os.environ["DB_PATH"])
    if db_path.exists():
        db_path.unlink()
    init_db()
    seed_if_empty()
    yield


@pytest.fixture
def client(fresh_db):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_client(client):
    r = client.post(
        "/login",
        data={"eposta": "admin@backrows.local", "sifre": "Admin123!"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    return client


@pytest.fixture
def katilimci_client(client):
    r = client.post(
        "/login",
        data={"eposta": "katilimci@backrows.local", "sifre": "Katilimci123!"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    return client


@pytest.fixture
def ziyaretci_client(client):
    r = client.post(
        "/login",
        data={"eposta": "ziyaretci@backrows.local", "sifre": "Ziyaretci123!"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    return client
