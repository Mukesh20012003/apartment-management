# backend/app/repositories/base_repository.py
from typing import Generic, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.base import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Generic repository for CRUD operations"""

    def __init__(self, model: type[T], db: Session):
        self.model = model
        self.db = db

    def create(self, obj_in: dict) -> T:
        """Create new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def read(self, id: Any) -> Optional[T]:
        """Get record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def read_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: Any, obj_in: dict) -> Optional[T]:
        """Update record"""
        db_obj = self.read(id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """Delete record"""
        db_obj = self.read(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """Count total records"""
        return self.db.query(self.model).count()

    def exists(self, **filters) -> bool:
        """Check if record exists"""
        return self.db.query(self.model).filter_by(**filters).first() is not None

    def filter(self, **filters) -> List[T]:
        """Filter records"""
        return self.db.query(self.model).filter_by(**filters).all()

    def filter_one(self, **filters) -> Optional[T]:
        """Get one record by filter"""
        return self.db.query(self.model).filter_by(**filters).first()
