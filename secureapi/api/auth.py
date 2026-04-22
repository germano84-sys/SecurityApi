from fastapi import APIRouter, Depends

from secureapi.clases.schemas import (
    FcmTokenUpdateRequest,
    FcmTokenUpdateResponse,
    LoginRequest,
    MasterTokenRequest,
    RegisterRequest,
    RoleListResponse,
    RoleResponse,
    RoleCreateRequest,
    RoleUpdateRequest,
    TokenResponse,
    UserInactiveResponse,
    UserListResponse,
    UserResponse,
)
from secureapi.core.security import get_current_user, require_admin, require_admin_master_key, require_supervisor_or_admin
from secureapi.repositories.user_repository import list_roles, list_users
from secureapi.services.auth_service import (
    create_role_entry,
    generate_token_for_user,
    login_user,
    register_user,
    set_user_inactive,
    set_user_role,
)
from secureapi.services.notification_service import set_runtime_fcm_device_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", summary="Registrar usuario", response_model=UserResponse)
def register(
    payload: RegisterRequest,
    current_user=Depends(require_supervisor_or_admin),
):
    return register_user(payload.username, payload.password, payload.role, current_user)


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
    _=Depends(require_admin),
):
    return set_user_role(username, payload.role)


@router.post("/roles", summary="Crear rol en catalogo", response_model=RoleResponse)
def create_role(payload: RoleCreateRequest, _=Depends(require_admin)):
    return create_role_entry(payload.name, payload.description)


@router.get("/roles", summary="Listar roles del catalogo", response_model=RoleListResponse)
def roles(_=Depends(require_supervisor_or_admin)):
    return {"roles": list_roles()}


@router.get("/users", summary="Listar usuarios activos", response_model=UserListResponse)
def users(_=Depends(require_supervisor_or_admin)):
    return {"users": list_users()}


@router.patch("/users/{username}/inactive", summary="Inactivar usuario (auditoria)", response_model=UserInactiveResponse)
def inactivate_user(username: str, _=Depends(require_admin)):
    return set_user_inactive(username)


@router.post("/fcm-token", summary="Registrar token FCM del navegador", response_model=FcmTokenUpdateResponse)
def register_fcm_token(payload: FcmTokenUpdateRequest, _=Depends(get_current_user)):
    return set_runtime_fcm_device_token(payload.token)
