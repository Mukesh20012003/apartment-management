# backend/app/repositories/user_repository.py
from app.repositories.base_repository import BaseRepository
from app.models.user import User
from sqlalchemy.orm import Session
from typing import Optional

class UserRepository(BaseRepository[User]):
    """User-specific repository"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.filter_one(email=email)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.filter_one(username=username)

    def get_active_users(self, skip: int = 0, limit: int = 100):
        """Get active users"""
        return self.db.query(self.model).filter(
            self.model.is_active == True
        ).offset(skip).limit(limit).all()

    def deactivate_user(self, user_id) -> Optional[User]:
        """Deactivate user"""
        return self.update(user_id, {"is_active": False})

    def verify_user(self, user_id) -> Optional[User]:
        """Mark user as verified"""
        return self.update(user_id, {"is_verified": True})
