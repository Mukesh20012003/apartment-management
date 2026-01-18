from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

from jose import JWTError, jwt 
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")



class SecurityUtils:
    """Security utilities for password and JWT handling."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage."""
        # UserRegister already enforces max_length=72
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against the stored hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: Dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            return payload
        except JWTError as exc:
            logger.warning("JWT verification failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
