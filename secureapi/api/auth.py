from fastapi import APIRouter, Depends

from clases.schemas import MasterTokenRequest, LoginRequest, RegisterRequest, RoleUpdateRequest, TokenResponse, UserResponse
from core.security import get_current_user, require_admin, require_admin_master_key, require_super_admin
from repositories.user_repository import list_users
from services.auth_service import generate_token_for_user, login_user, register_user, set_user_inactive, set_user_role

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", summary="Registrar usuario", response_model=UserResponse)
def register(
    payload: RegisterRequest,
    _=Depends(require_admin),
):
    return register_user(payload.username, payload.password)


@router.post("/login", summary="Iniciar sesion", response_model=TokenResponse)
def login(payload: LoginRequest):
    return login_user(payload.username, payload.password)


@router.post("/master-token", summary="Generar token con clave maestra", response_model=TokenResponse)
def master_token(payload: MasterTokenRequest, _=Depends(require_admin_master_key)):
    return generate_token_for_user(payload.username)


@router.get("/me", summary="Usuario autenticado", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "role": current_user["role"],
    }


@router.patch("/users/{username}/role", summary="Asignar rol a usuario", response_model=UserResponse)
def update_role(
    username: str,
    payload: RoleUpdateRequest,
    _=Depends(require_super_admin),
):
    return set_user_role(username, payload.role)


@router.get("/users", summary="Listar usuarios activos")
def users(_=Depends(require_admin)):
    return {"users": list_users()}


@router.patch("/users/{username}/inactive", summary="Inactivar usuario (auditoria)")
def inactivate_user(username: str, _=Depends(require_super_admin)):
    return set_user_inactive(username)
