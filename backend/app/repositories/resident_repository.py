# backend/app/repositories/resident_repository.py
from app.repositories.base_repository import BaseRepository
from app.models.resident import Resident, Flat
from app.core.constants import ResidentStatus
from sqlalchemy.orm import Session
from typing import Optional, List

class FlatRepository(BaseRepository[Flat]):
    def __init__(self, db: Session):
        super().__init__(Flat, db)

    def get_by_flat_number(self, flat_number: str) -> Optional[Flat]:
        return self.filter_one(flat_number=flat_number)

class ResidentRepository(BaseRepository[Resident]):
    """Resident-specific repository"""

    def __init__(self, db: Session):
        super().__init__(Resident, db)

    def get_by_user(self, user_id) -> Optional[Resident]:
        """Get resident by user ID"""
        return self.filter_one(user_id=user_id)

    def get_pending_approvals(self, skip: int = 0, limit: int = 50) -> List[Resident]:
        """Get pending resident approvals"""
        return self.db.query(self.model).filter(
            self.model.status == ResidentStatus.PENDING
        ).offset(skip).limit(limit).all()

    def approve_resident(self, resident_id) -> Optional[Resident]:
        """Approve resident"""
        return self.update(resident_id, {"status": ResidentStatus.APPROVED})

    def reject_resident(self, resident_id, notes: str) -> Optional[Resident]:
        """Reject resident"""
        return self.update(resident_id, {
            "status": ResidentStatus.REJECTED,
            "approval_notes": notes
        })
