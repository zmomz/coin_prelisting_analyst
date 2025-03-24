"""API endpoints for managing user accounts."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_manager
from app.crud.users import delete_user, get_user, get_users, update_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
):
    """Retrieve user details (manager only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/", response_model=list[UserOut])
async def get_users_endpoint(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
    skip: int = 0,
    limit: int = 100,
):
    """List all users (manager only)."""
    return await get_users(db, skip, limit)


@router.put("/{user_id}", response_model=UserOut)
async def update_user_endpoint(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
):
    """Update user details (manager only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await update_user(db, user, user_in)


@router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
):
    """Soft delete a user (manager only)."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await delete_user(db, user)
    return {"detail": "User deleted successfully"}
