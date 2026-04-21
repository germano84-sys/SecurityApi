from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "SecurityApi",
        },
    )


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "title": "SecurityApi Dashboard",
            "task_states": ["no_iniciada", "en_proceso", "cumplida"],
            "role_options": ["admin", "supervisor", "usuario_comun"],
        },
    )


@router.get("/firebase-messaging-sw.js", include_in_schema=False)
def firebase_service_worker():
    return FileResponse(BASE_DIR / "static" / "firebase-messaging-sw.js")
