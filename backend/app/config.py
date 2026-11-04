import os
import sys
from pathlib import Path

# Paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
BASE_DIR = BACKEND_DIR.parent
ENV_PATH = BASE_DIR / ".env"

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except ImportError:
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

def _resolve_path(env_val: str | None, default_path: Path) -> Path:
    if not env_val:
        return default_path
    p = Path(env_val)
    return p if p.is_absolute() else (BASE_DIR / p).resolve()

# Application & Server Config
APP_NAME = os.environ.get("APP_NAME", "GST Billing Software")
APP_ENV = os.environ.get("APP_ENV", "production")
APP_HOST = os.environ.get("APP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("APP_PORT", "47371"))
AUTO_OPEN_BROWSER = os.environ.get("AUTO_OPEN_BROWSER", "true").lower() in ("true", "1", "yes")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")

# Directory Config
DATA_DIR = _resolve_path(os.environ.get("DATA_DIR") or os.environ.get("FREEGSTBILL_DATA"), BASE_DIR / "data")
INVOICES_DIR = _resolve_path(os.environ.get("INVOICES_DIR") or os.environ.get("FREEGSTBILL_INVOICES"), BASE_DIR / "Saved Invoices")
FRONTEND_DIST = _resolve_path(os.environ.get("FRONTEND_DIST"), BASE_DIR / "frontend" / "dist")
CHANGELOG_PATH = (BASE_DIR / "docs" / "CHANGELOG.md") if (BASE_DIR / "docs" / "CHANGELOG.md").exists() else (BASE_DIR / "CHANGELOG.md")
PACKAGE_JSON_PATH = BASE_DIR / "package.json"

# Database Configuration (PostgreSQL)
DB_ENABLED = os.environ.get("DB_ENABLED", "true").lower() in ("true", "1", "yes")
DB_ENGINE = os.environ.get("DB_ENGINE", "postgresql")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "12345")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "GST-Billing")
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Operational Thresholds
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "5"))
BACKUP_RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
RATE_LIMIT_MAX_ATTEMPTS = int(os.environ.get("RATE_LIMIT_MAX_ATTEMPTS", "5"))
RATE_LIMIT_LOCKOUT_SECONDS = int(os.environ.get("RATE_LIMIT_LOCKOUT_SECONDS", "30"))

# CORS
raw_cors = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in raw_cors.split(",") if o.strip()] or [
    "http://localhost:47371",
    "http://127.0.0.1:47371",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
PORT_FILE = DATA_DIR / "port.txt"
ERRORS_LOG = DATA_DIR / "errors.log"
META_PATH = DATA_DIR / "meta.json"
PROFILE_PATH = DATA_DIR / "profile.json"
LOCAL_PREFS_PATH = DATA_DIR / "local-prefs.json"
BACKUPS_DIR = DATA_DIR / "backups"
BILL_TRASH_DIR = DATA_DIR / "trash"
PDF_ORIGINALS_DIR = DATA_DIR / "cancelled-pdf-originals"

DIRS = [
    "bills",
    "clients",
    "templates",
    "products",
    "expenses",
    "recurring",
    "receipts",
    "profiles",
    "purchases",
    "productions",
    "purchase-orders",
    "cash-book"
]

LOCK_KEY = "appLock"
BACKUP_FOLDER_KEY = "backupFolder"
EXTRA_BACKUP_SUBDIR = "FreeGSTBill Daily Backups"

DEFAULT_PROFILE = {
    "businessName": "",
    "address": "",
    "state": "",
    "gstin": "",
    "pan": "",
    "email": "",
    "phone": "",
    "bankName": "",
    "accountNumber": "",
    "ifsc": "",
    "logo": "",
    "signature": "",
    "upiId": "",
    "googleClientId": "",
    "googleDriveFolder": "GST Billing Invoices",
}

def ensure_directories():
    """Ensure data subdirectories exist on startup."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        INVOICES_DIR.mkdir(parents=True, exist_ok=True)
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        BILL_TRASH_DIR.mkdir(parents=True, exist_ok=True)
        PDF_ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
        for d in DIRS:
            (DATA_DIR / d).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        sys.stderr.write(f"Failed to create data directory: {e}\n")
        raise
