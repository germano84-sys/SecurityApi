from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from secureapi.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_MASTER_KEY, ALGORITHM, SECRET_KEY
from secureapi.repositories.user_repository import get_user_by_username

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password, stored_password_hash):
    return bcrypt.checkpw(plain_password.encode(), stored_password_hash.encode())


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials or credentials.scheme.lower() != "bearer":
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(username)
    if not user:
        raise credentials_exception
    return user


def require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol admin")
    return current_user


def require_supervisor_or_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") not in {"admin", "supervisor"}:
        raise HTTPException(status_code=403, detail="Se requiere rol supervisor o admin")
    return current_user


def require_usuario_comun(current_user=Depends(get_current_user)):
    if current_user.get("role") != "usuario_comun":
        raise HTTPException(status_code=403, detail="Se requiere rol usuario_comun")
    return current_user


def require_admin_master_key(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    if not ADMIN_MASTER_KEY:
        raise HTTPException(status_code=500, detail="ADMIN_MASTER_KEY no configurada")

    if not x_admin_key or x_admin_key != ADMIN_MASTER_KEY:
        raise HTTPException(status_code=403, detail="X-Admin-Key invalida")

    return True
