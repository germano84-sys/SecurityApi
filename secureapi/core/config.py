import os
from pathlib import Path

from dotenv import load_dotenv

SECUREAPI_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SECUREAPI_DIR.parent

# Load both env locations to support running from root or secureapi dir.
load_dotenv(PROJECT_ROOT / ".env", override=True)
load_dotenv(SECUREAPI_DIR / ".env", override=True)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_MASTER_KEY = os.getenv("ADMIN_MASTER_KEY")


def _get_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


EMAIL_NOTIFICATIONS_ENABLED = _get_bool("EMAIL_NOTIFICATIONS_ENABLED", "false")
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_SMTP_USER = os.getenv("EMAIL_SMTP_USER", "")
EMAIL_SMTP_PASSWORD = os.getenv("EMAIL_SMTP_PASSWORD", "")
EMAIL_SMTP_USE_TLS = _get_bool("EMAIL_SMTP_USE_TLS", "true")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_SMTP_USER)
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", "SecurityApi")

FCM_ENABLED = _get_bool("FCM_ENABLED", "false")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")
FCM_DEVICE_TOKEN = os.getenv("FCM_DEVICE_TOKEN", "")
