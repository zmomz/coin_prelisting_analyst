import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.crud.users import get_user, get_users, update_user, delete_user
from app.schemas.user import UserUpdate, UserOut
from app.api.deps import get_current_user, get_current_manager

router = APIRouter()


@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(
    user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """Managers can retrieve user details."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=List[UserOut])
async def get_users_endpoint(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_manager),
    skip: int = 0, 
    limit: int = 100
):
    """Managers can list all users."""
    return await get_users(db, skip, limit)


@router.put("/{user_id}", response_model=UserOut)
async def update_user_endpoint(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_manager),
):
    """Managers can update user details."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return await update_user(db, user, user_in)


@router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """Managers can soft delete users."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await delete_user(db, user)
    return {"detail": "User deleted successfully"}
