import os
from fastapi import FastAPI

from api.auth import router as auth_router
from api.scanner import router as scanner_router
from api.tasks import router as tasks_router
from database.database import init_db
from services.auth_service import bootstrap_admin

init_db()

app = FastAPI(
    title="SecureAPI - Escáner de Vulnerabilidades y Cifrado",
    description="API para análisis de seguridad web (cabeceras, endpoints, HTTPS) y servicios de hashing.",
    version="1.1.0",
)


@app.on_event("startup")
def startup_events():
    bootstrap_admin()


app.include_router(auth_router)
app.include_router(scanner_router)
app.include_router(tasks_router)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "true").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload_enabled)
