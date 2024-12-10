from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, club_id: Optional[str] = None):
    """
    Genera un token de acceso JWT con datos adicionales como el `club_id`.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Si se proporciona un `club_id`, inclúyelo en el token
    if club_id:
        to_encode.update({"club_id": club_id})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)

    # Validar si hay datos básicos en el payload
    if "sub" not in payload or "user_type" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Retorna el payload completo
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "user_type": payload.get("user_type"),
        "club_id": payload.get("club_id"),  # Podría ser None si no aplica
    }