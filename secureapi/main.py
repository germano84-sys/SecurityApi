import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from secureapi.api.auth import router as auth_router
from secureapi.api.scanner import router as scanner_router
from secureapi.api.tasks import router as tasks_router
from secureapi.api.web import router as web_router
from secureapi.database.database import init_db
from secureapi.services.auth_service import bootstrap_admin

init_db()

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_admin()
    yield

app = FastAPI(
    title="SecureAPI - Escáner de Vulnerabilidades y Cifrado",
    description="API para análisis de seguridad web (cabeceras, endpoints, HTTPS) y servicios de hashing.",
    version="1.1.0",
    lifespan=lifespan,
)


app.include_router(auth_router)
app.include_router(scanner_router)
app.include_router(tasks_router)
app.include_router(web_router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


if __name__ == "__main__":
    import sys
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "true").lower() == "true"
    sys.path.insert(0, str(BASE_DIR.parent))
    uvicorn.run("secureapi.main:app", host=host, port=port, reload=reload_enabled)
