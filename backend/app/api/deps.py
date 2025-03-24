"""Dependency functions for API endpoints."""

import uuid
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.crud.users import get_user
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Extract user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning("JWT payload missing 'sub'")
            raise credentials_exception

        user_uuid = uuid.UUID(user_id)

    except (JWTError, ValueError) as e:
        logger.warning(f"Token validation failed: {e}")
        raise credentials_exception
    except Exception:
        logger.exception("Unexpected error during JWT decoding")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error"
        )

    user = await get_user(db, user_uuid)

    if user is None:
        logger.warning(f"User ID {user_uuid} not found in DB")
        raise credentials_exception

    if not user.is_active:
        logger.warning(f"User {user.email} is inactive")
        raise HTTPException(status_code=403, detail="Inactive user")

    return user


async def get_current_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    """Restrict access to managers only."""
    if current_user.role != UserRole.MANAGER:
        logger.warning(
            f"Access denied: {current_user.email} \
                ({current_user.role}) is not a manager"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
