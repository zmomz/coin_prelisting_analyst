from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict | str | uuid.UUID, expires_delta: int = None):
    """Generate JWT access token."""
    if isinstance(data, (str, uuid.UUID)):
        to_encode = {"sub": str(data)}
    else:
        to_encode = data.copy()

    expires_delta = settings.ACCESS_TOKEN_EXPIRE_MINUTES if expires_delta is None else expires_delta
    if isinstance(expires_delta, timedelta):
        expires_delta = int(expires_delta.total_seconds() / 60)

    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
