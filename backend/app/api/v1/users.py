"""API endpoints for managing user accounts."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_manager
from app.crud.users import delete_user, get_user, get_users, update_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
        "/{user_id}",
        response_model=UserOut,
        status_code=status.HTTP_200_OK
)
async def get_user_endpoint(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
) -> UserOut:
    """Retrieve a single user by ID (manager only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK)
async def get_users_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
) -> List[UserOut]:
    """List all users (manager only)."""
    return await get_users(db, skip, limit)


@router.put(
        "/{user_id}",
        response_model=UserOut,
        status_code=status.HTTP_200_OK
)
async def update_user_endpoint(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
) -> UserOut:
    """Update user details (manager only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return await update_user(db, user, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_endpoint(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
) -> dict:
    """Soft delete a user (manager only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await delete_user(db, user)
    return {"detail": "User deleted successfully"}
