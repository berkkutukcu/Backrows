import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "data" / "backrows.db"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "data" / "uploads"))
ANNOUNCEMENTS_DIR = UPLOAD_DIR / "announcements"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

SECRET_KEY = os.getenv("SECRET_KEY", "dev-gizli-anahtar-uretim-ortaminda-degistir")

EMAIL_CODE_TTL_SECONDS = 15 * 60
ANNOUNCEMENT_SLOTS = 5
ANNOUNCEMENT_SIZE = (400, 400)

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
ANNOUNCEMENTS_DIR.mkdir(parents=True, exist_ok=True)
