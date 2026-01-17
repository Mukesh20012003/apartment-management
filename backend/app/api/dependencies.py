# backend/app/api/dependencies.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import SecurityUtils, oauth2_scheme
from app.database.session import get_db
from app.models.user import User
from app.core.constants import UserRole
from app.repositories.user_repository import UserRepository


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = SecurityUtils.verify_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = UserRepository(db).get_by_email(email=email)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to enforce role-based access.
    Use as: current_admin = Depends(require_role(UserRole.ADMIN)).
    """

    async def _role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        return current_user

    return _role_checker
