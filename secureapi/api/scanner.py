from fastapi import APIRouter, Depends

from secureapi.clases.schemas import HashResponse, ScanHistoryResponse, ScanResponse
from secureapi.core.security import get_current_user
from secureapi.crypto.hash import hash_bcrypt, hash_sha256
from secureapi.repositories.scan_repository import get_all_scans
from secureapi.services.scan_service import scan_url_for_user

router = APIRouter(tags=["security"])


@router.get("/escanear", summary="Escanear sitio web", response_model=ScanResponse)
def escanear(url: str, current_user=Depends(get_current_user)):
    return scan_url_for_user(url, current_user)


@router.post("/hash/sha256", summary="Generar hash SHA256", response_model=HashResponse)
def sha256(data: str, _=Depends(get_current_user)):
    return {"hash": hash_sha256(data)}


@router.post("/hash/bcrypt", summary="Generar hash bcrypt", response_model=HashResponse)
def bcrypt_hash(data: str, _=Depends(get_current_user)):
    return {"hash": hash_bcrypt(data)}


@router.get("/historial", summary="Ver historial de escaneos", response_model=ScanHistoryResponse)
def historial(current_user=Depends(get_current_user)):
    if current_user["role"] == "usuario_comun":
        return {"registros": get_all_scans(performed_by=current_user["id"])}
    return {"registros": get_all_scans()}
