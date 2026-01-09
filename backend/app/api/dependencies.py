from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token  # your JWT decode helper
from app.models.user import User                   # your SQLAlchemy/Pydantic user model
from app.services.user_service import UserService         # your service layer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_user_service() -> UserService:
    """
    Dependency that returns a UserService instance.
    Adjust constructor args (session, repositories) to your project.
    """
    return UserService()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """
    Get the currently authenticated user from the JWT access token.
    """
    try:
        token_data = decode_access_token(token)  # should raise if invalid/expired
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_by_id(token_data.sub)  # or token_data.user_id/email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


def require_role(*allowed_roles: str):
    """
    Factory that returns a dependency enforcing that the current user has one
    of the allowed roles.
    """

    async def _role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return _role_checker
