import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from forge.core.config import get_settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def _decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """FastAPI dependency to verify Bearer token from Authorization header."""
    token = credentials.credentials
    payload = _decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encrypt_pat(pat: str) -> str:
    settings = get_settings()
    key = settings.pat_encryption_key.encode() if isinstance(settings.pat_encryption_key, str) else settings.pat_encryption_key
    cipher = Fernet(key)
    return cipher.encrypt(pat.encode()).decode()


def decrypt_pat(encrypted_pat: str) -> str:
    settings = get_settings()
    key = settings.pat_encryption_key.encode() if isinstance(settings.pat_encryption_key, str) else settings.pat_encryption_key
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_pat.encode()).decode()
