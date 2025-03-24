from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.core.security import create_access_token, verify_password
from app.crud.users import create_user, get_user_by_email
from app.db.session import get_db
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token."""
    normalized_email = login_data.email.strip().lower()
    user = await get_user_by_email(db, normalized_email)

    if not user or not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for {normalized_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    logger.info(f"User {user.email} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    normalized_email = user_in.email.strip().lower()

    existing_user = await get_user_by_email(db, normalized_email)
    if existing_user:
        logger.warning(f"Attempt to register with existing email: {normalized_email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_in.email = normalized_email  # Normalize for creation
    new_user = await create_user(db, user_in)
    logger.info(f"Registered new user: {new_user.email} (role={new_user.role})")

    return new_user
