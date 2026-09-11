from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

from app.core.config import config


password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Метод для получение захешированного пароля"""
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Метод для верификация пароля"""
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id: int) -> str:
    """Создание jwt token"""
    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )