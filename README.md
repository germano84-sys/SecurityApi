# SecureAPI

Security scanning and vulnerability assessment API built with FastAPI.

## Quick Start

### Prerequisites
- Python 3.11+
- make (optional, but recommended)

### Installation & Running

```bash
make run
```

That's it. A fresh clone only needs that command. The first time it will:
1. Create a Python virtual environment
2. Install all dependencies from `requirements.txt`
3. Start the API on http://127.0.0.1:8007

### Configuration

All settings are in `.env`:

```dotenv
SECRET_KEY=dev-change-me-please-very-long-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_USERNAME=luisg
ADMIN_PASSWORD=12345
HOST=127.0.0.1
PORT=8000
```

### Firebase Setup

To enable Firebase Cloud Messaging notifications:

1. Download your Firebase service account JSON from [Firebase Console](https://console.firebase.google.com/)
2. Place it at: `secureapi/keys/firebase-service-account.json`
3. Enable FCM in `.env`:
   ```dotenv
   FCM_ENABLED=true
   FIREBASE_SERVICE_ACCOUNT_PATH=secureapi/keys/firebase-service-account.json
   ```

If you do not add the Firebase JSON, the app still starts and runs with FCM disabled by default.

### Project Structure

```
.
├── run_api.py              # Main entry point (handles venv + deps)
├── Makefile                # Quick commands
├── .env                    # Configuration
└── secureapi/
    ├── main.py             # FastAPI app
    ├── requirements.txt    # Python dependencies
    ├── api/                # API endpoints
    ├── services/           # Business logic
    ├── database/           # DB layer
    ├── keys/               # Firebase credentials (add here)
    └── templates/          # HTML templates
```

## Development

- API runs with hot reload enabled (changes trigger automatic restart)
- Database: SQLite (`secureapi/scans.db`)
- Logs and output shown in terminal

## Troubleshooting

**"Permission denied" on start_api.sh:**
```bash
chmod +x start_api.sh
```

**Python not found:**
Ensure Python 3.11+ is installed and in PATH, or use `uv`:
```bash
uv run --python 3.11 run_api.py
```
