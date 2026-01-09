# backend/app/api/v1/users.py
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserUpdate,  # make sure this schema exists
)
from app.core.security import SecurityUtils
from app.core.exceptions import InvalidCredentials
from app.models.user import User
from app.config import settings

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def get_user_service(db: Session) -> UserService:
    """Helper to build UserService from DB session."""
    repository = UserRepository(db)
    return UserService(repository, db)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserRegister,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Register a new user.
    """
    service = get_user_service(db)

    user = service.register_user(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password=user_data.password,
        phone_number=user_data.phone_number,
        role=user_data.role,
    )

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Login user and return access token.
    """
    service = get_user_service(db)

    try:
        user = service.authenticate_user(
            credentials.email,
            credentials.password,
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = SecurityUtils.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get current authenticated user info.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Update the current authenticated user.
    """
    service = get_user_service(db)

    updated_user = service.update(
        current_user.id,
        user_update.dict(exclude_unset=True),
    )

    return updated_user
