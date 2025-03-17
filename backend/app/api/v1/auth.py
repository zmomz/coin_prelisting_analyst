from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud.users import create_user, get_user_by_email
from app.db.session import get_db
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login", response_model=Token)
async def login_user(
    login_data: LoginRequest,  # Accept JSON
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    user = await get_user_by_email(db, login_data.email)  # Use email instead of username
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    print(f"🔍 Registering user: {user_in.email}, Role: {user_in.role}")  # Debug Log

    try:
        user = await get_user_by_email(db, user_in.email)
        if user:
            print(f"⚠️ User already exists: {user_in.email}")  # Debug Log
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = await create_user(db, user_in)
        print(f"✅ User created: {user.email}, Role: {user.role}")  # Debug Log
        return user

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(f"🚨 FULL ERROR TRACEBACK: \n{error_message}")  # Debug Log
        raise HTTPException(status_code=500, detail=str(e))  # Show real error
