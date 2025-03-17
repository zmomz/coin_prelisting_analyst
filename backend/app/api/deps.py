"""Dependency functions for API endpoints."""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.users import get_user
from app.db.session import get_db
from app.models.user import User, UserRole
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


logger = logging.getLogger(__name__)


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Get the currently authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    if not token:  # ✅ Handle missing token properly
        logger.warning("❌ No token provided, returning 401 Unauthorized.")
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print("🔍 Decoded Token Payload:", payload)
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error("🚨 JWT Decoding Failed: No user_id found in token")
            raise credentials_exception
    except JWTError:
        print("🚨 JWT Decoding Failed!")
        logger.error("🚨 JWT Decoding Failed: Invalid Token")
        raise credentials_exception
    except Exception as e:
        logger.error(f"🚨 Unexpected JWT error: {e}")
        raise HTTPException(status_code=500, detail="Internal authentication error")

    logger.info(f"🔍 Retrieving user from DB with ID: {user_id}")
    user = await get_user(db, uuid.UUID(user_id))

    if user is None:
        logger.error(f"❌ User not found in DB for ID: {user_id}")
        raise credentials_exception

    if not user.is_active:
        logger.error(f"❌ User {user.email} is deactivated!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    logger.info(f"✅ User Retrieved: {user.email}, Role: {user.role}")
    return user



async def get_current_manager(current_user: User = Depends(get_current_user)) -> User:
    """Get the currently authenticated manager user."""
    
    if current_user is None:
        logger.error("🚨 ERROR: No current user retrieved!")
        raise HTTPException(status_code=401, detail="User not authenticated")

    if not hasattr(current_user, "role"):
        logger.error(f"🚨 ERROR: User object missing role! User={current_user}")
        raise HTTPException(status_code=500, detail="User role is missing")

    logger.info(f"🔍 Checking Manager Access: {current_user.email}, Role: {current_user.role}")

    if current_user.role is None:
        logger.error(f"🚨 ERROR: User role is None! User={current_user}")
        raise HTTPException(status_code=500, detail="User role is missing")

    if current_user.role != UserRole.MANAGER:
        logger.warning(f"❌ ACCESS DENIED: {current_user.email} is {current_user.role}, not a manager!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    logger.info("✅ Access Granted: User is a manager.")
    return current_user

