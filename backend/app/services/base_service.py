# backend/app/services/base_service.py
from abc import ABC, abstractmethod
from typing import Optional, List, Any
from sqlalchemy.orm import Session

class IService(ABC):
    """Interface defining service contract (Interface Segregation)"""
    
    @abstractmethod
    def create(self, data: dict) -> Any:
        pass
    
    @abstractmethod
    def read(self, id: Any) -> Optional[Any]:
        pass
    
    @abstractmethod
    def update(self, id: Any, data: dict) -> Optional[Any]:
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        pass

class BaseService(IService):
    """Base service class (Single Responsibility)"""
    
    def __init__(self, repository, db: Session):
        self.repository = repository
        self.db = db

    def create(self, data: dict) -> Any:
        return self.repository.create(data)

    def read(self, id: Any) -> Optional[Any]:
        return self.repository.read(id)

    def update(self, id: Any, data: dict) -> Optional[Any]:
        return self.repository.update(id, data)

    def delete(self, id: Any) -> bool:
        return self.repository.delete(id)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.read_all(skip, limit)
