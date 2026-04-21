from fastapi import HTTPException

from secureapi.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_PASSWORD, ADMIN_USERNAME
from secureapi.core.security import create_access_token, verify_password
from secureapi.crypto.hash import hash_bcrypt
from secureapi.repositories.user_repository import (
    create_role,
    create_user,
    deactivate_user,
    get_user_by_username,
    list_roles,
    upsert_admin_user,
    update_user_role,
)


def bootstrap_admin():
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return

    password_hash = hash_bcrypt(ADMIN_PASSWORD)
    upsert_admin_user(ADMIN_USERNAME, password_hash)


def create_role_entry(name: str, description: str):
    normalized = name.strip().lower()
    if any(role["name"] == normalized for role in list_roles()):
        raise HTTPException(status_code=409, detail="El rol ya existe")

    role_id = create_role(normalized, description)
    return {"id": role_id, "name": normalized, "description": description}


def register_user(username: str, password: str, role: str, current_user: dict):
    if get_user_by_username(username):
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    requested_role = role.strip().lower()
    requester_role = current_user["role"]

    if requester_role == "supervisor" and requested_role != "usuario_comun":
        raise HTTPException(
            status_code=403,
            detail="Un supervisor solo puede registrar usuarios con rol usuario_comun",
        )

    if requester_role == "admin" and requested_role not in {entry["name"] for entry in list_roles()}:
        raise HTTPException(status_code=400, detail="El rol solicitado no existe en el catalogo")

    password_hash = hash_bcrypt(password)
    try:
        user_id = create_user(username, password_hash, requested_role, created_by=current_user["id"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"id": user_id, "username": username, "role": requested_role}


def set_user_role(username: str, role: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if role.strip().lower() not in {entry["name"] for entry in list_roles()}:
        raise HTTPException(status_code=400, detail="Rol no registrado en catalogo")

    if not update_user_role(username, role):
        raise HTTPException(status_code=400, detail="No fue posible actualizar el rol")

    updated_user = get_user_by_username(username)
    return {
        "id": updated_user["id"],
        "username": updated_user["username"],
        "role": updated_user["role"],
    }


def set_user_inactive(username: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user["role"] == "admin":
        raise HTTPException(status_code=403, detail="No se puede inactivar un usuario admin")

    if not deactivate_user(username):
        raise HTTPException(status_code=400, detail="No se pudo inactivar el usuario")

    return {"message": "Usuario inactivado", "username": username}


def login_user(username: str, password: str):
    username = (username or "").strip()
    password = (password or "").strip()

    # Ensure env-configured admin can always authenticate even if DB state is stale.
    if (
        ADMIN_USERNAME
        and ADMIN_PASSWORD
        and username == ADMIN_USERNAME.strip()
        and password == ADMIN_PASSWORD
    ):
        upsert_admin_user(ADMIN_USERNAME.strip(), hash_bcrypt(ADMIN_PASSWORD))

    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    access_token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
    }


def generate_token_for_user(username: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="La clave maestra solo puede generar token para admin")

    access_token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
    }
