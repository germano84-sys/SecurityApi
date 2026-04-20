from fastapi import HTTPException

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_PASSWORD, ADMIN_USERNAME
from core.security import create_access_token, verify_password
from crypto.hash import hash_bcrypt
from repositories.user_repository import create_user, deactivate_user, get_user_by_username, update_user_role


def bootstrap_admin():
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return

    existing_user = get_user_by_username(ADMIN_USERNAME)
    if existing_user:
        return

    password_hash = hash_bcrypt(ADMIN_PASSWORD)
    create_user(ADMIN_USERNAME, password_hash, "super_admin")


def register_user(username: str, password: str):
    if get_user_by_username(username):
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    password_hash = hash_bcrypt(password)
    user_id = create_user(username, password_hash, "usuario")
    return {"id": user_id, "username": username, "role": "usuario"}


def set_user_role(username: str, role: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_user_role(username, role)
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

    if user["role"] == "super_admin":
        raise HTTPException(status_code=403, detail="No se puede inactivar al super_admin")

    if not deactivate_user(username):
        raise HTTPException(status_code=400, detail="No se pudo inactivar el usuario")

    return {"message": "Usuario inactivado", "username": username}


def login_user(username: str, password: str):
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

    access_token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
    }
