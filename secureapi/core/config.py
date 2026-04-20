import os
from pathlib import Path

from dotenv import load_dotenv

SECUREAPI_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SECUREAPI_DIR.parent

# Load both env locations to support running from root or secureapi dir.
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(SECUREAPI_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
	raise ValueError("Falta SECRET_KEY en variables de entorno (.env)")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_MASTER_KEY = os.getenv("ADMIN_MASTER_KEY")
