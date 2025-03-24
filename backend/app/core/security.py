import uuid
from datetime import datetime, timedelta
from typing import Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Algorithm
ALGORITHM = "HS256"


def create_access_token(
    data: Union[dict, str, uuid.UUID],
    expires_delta: Union[int, timedelta, None] = None,
) -> str:
    """Generate a JWT access token."""
    payload = {"sub": str(data)} if isinstance(data, (str, uuid.UUID)) else data.copy()

    # Default to settings value if not provided
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    elif isinstance(expires_delta, int):
        expires_delta = timedelta(minutes=expires_delta)

    expire = datetime.now() + expires_delta
    payload.update({"exp": expire})

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)
