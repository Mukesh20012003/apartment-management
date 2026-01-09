# backend/app/services/resident_service.py
from app.services.base_service import BaseService
from app.repositories.resident_repository import ResidentRepository, FlatRepository
from app.core.constants import ResidentStatus
from app.core.exceptions import AppException, InvalidData
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class ResidentService(BaseService):
    """Resident service (Single Responsibility)"""
    
    def __init__(self, repository: ResidentRepository, db: Session):
        super().__init__(repository, db)
        self.repository = repository
        self.flat_repository = FlatRepository(db)

    def register_resident(
        self,
        user_id: UUID,
        flat_id: UUID,
        move_in_date: Optional[str] = None,
        family_members: int = 1,
        vehicle_details: Optional[str] = None,
        emergency_contact: Optional[str] = None
    ):
        """Register resident"""
        # Validate flat exists
        flat = self.flat_repository.read(flat_id)
        if not flat:
            raise InvalidData("Flat not found")

        resident_data = {
            "user_id": user_id,
            "flat_id": flat_id,
            "move_in_date": move_in_date,
            "family_members": family_members,
            "vehicle_details": vehicle_details,
            "emergency_contact": emergency_contact,
            "status": ResidentStatus.PENDING
        }

        resident = self.repository.create(resident_data)
        
        # Emit event for approval notification
        logger.info(f"Resident registered: {resident.id}")
        
        return resident

    def get_pending_approvals(self, skip: int = 0, limit: int = 50):
        """Get pending resident approvals"""
        return self.repository.get_pending_approvals(skip, limit)

    def approve_resident(self, resident_id: UUID, approval_notes: str = None):
        """Approve resident"""
        resident = self.repository.read(resident_id)
        if not resident:
            raise AppException("Resident not found")

        updated = self.repository.approve_resident(resident_id)
        
        # Emit event for approval notification
        logger.info(f"Resident approved: {resident_id}")
        
        return updated

    def reject_resident(self, resident_id: UUID, notes: str):
        """Reject resident"""
        resident = self.repository.read(resident_id)
        if not resident:
            raise AppException("Resident not found")

        updated = self.repository.reject_resident(resident_id, notes)
        
        # Emit event for rejection notification
        logger.info(f"Resident rejected: {resident_id}")
        
        return updated

    def get_resident_by_user(self, user_id: UUID):
        """Get resident by user ID"""
        return self.repository.get_by_user(user_id)
