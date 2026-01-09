# backend/app/services/user_service.py
from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import SecurityUtils
from app.core.exceptions import UserAlreadyExists, InvalidCredentials, UserNotFound
from app.core.constants import UserRole
from sqlalchemy.orm import Session
from typing import Optional

class UserService(BaseService):
    """User service (Single Responsibility, Dependency Injection)"""
    
    def __init__(self, repository: UserRepository, db: Session):
        super().__init__(repository, db)
        self.repository = repository

    def register_user(
        self,
        email: str,
        username: str,
        full_name: str,
        password: str,
        phone_number: Optional[str] = None,
        role: UserRole = UserRole.RESIDENT
    ) -> User:
        """Register new user"""
        # Check if user exists (DRY principle)
        if self.repository.get_by_email(email):
            raise UserAlreadyExists()

        if self.repository.get_by_username(username):
            raise UserAlreadyExists()

        # Hash password securely
        hashed_password = SecurityUtils.hash_password(password)

        user_data = {
            "email": email,
            "username": username,
            "full_name": full_name,
            "phone_number": phone_number,
            "hashed_password": hashed_password,
            "role": role
        }

        return self.repository.create(user_data)

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user and return user object"""
        user = self.repository.get_by_email(email)

        if not user or not SecurityUtils.verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        if not user.is_active:
            raise InvalidCredentials()

        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.repository.get_by_email(email)

    def update_user_password(self, user_id, new_password: str) -> User:
        """Update user password"""
        user = self.read(user_id)
        if not user:
            raise UserNotFound()

        hashed_password = SecurityUtils.hash_password(new_password)
        return self.repository.update(user_id, {"hashed_password": hashed_password})

    def get_active_users(self, skip: int = 0, limit: int = 100):
        """Get active users"""
        return self.repository.get_active_users(skip, limit)
