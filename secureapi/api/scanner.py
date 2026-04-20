from fastapi import APIRouter, Depends

from core.security import get_current_user, require_admin
from crypto.hash import hash_bcrypt, hash_sha256
from repositories.scan_repository import get_all_scans
from services.scan_service import scan_url

router = APIRouter(tags=["security"])


@router.get("/escanear", summary="Escanear sitio web")
def escanear(url: str, _=Depends(get_current_user)):
    return scan_url(url)


@router.post("/hash/sha256", summary="Generar hash SHA256")
def sha256(data: str, _=Depends(get_current_user)):
    return {"hash": hash_sha256(data)}


@router.post("/hash/bcrypt", summary="Generar hash bcrypt")
def bcrypt_hash(data: str, _=Depends(get_current_user)):
    return {"hash": hash_bcrypt(data)}


@router.get("/historial", summary="Ver historial de escaneos")
def historial(_=Depends(require_admin)):
    return {"registros": get_all_scans()}
