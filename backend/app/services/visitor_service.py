# backend/app/services/visitor_service.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.repositories.visitor_repository import VisitorLogRepository
from app.models.visitor import VisitorLog


class VisitorService:
    """Business logic for visitor logs"""

    def __init__(self, repository: VisitorLogRepository):
        self.repository = repository

    def create_entry(
        self,
        *,
        flat_id: UUID,
        security_id: UUID,
        visitor_name: str,
        visitor_phone: str,
        visitor_id_proof: str | None,
        purpose: str,
        vehicle_number: str | None,
        notes: str | None,
        entry_time: datetime | None = None,
    ) -> VisitorLog:
        data = {
            "flat_id": flat_id,
            "security_id": security_id,
            "visitor_name": visitor_name,
            "visitor_phone": visitor_phone,
            "visitor_id_proof": visitor_id_proof,
            "purpose": purpose,
            "vehicle_number": vehicle_number,
            "notes": notes,
            "entry_time": entry_time or datetime.utcnow(),
        }
        return self.repository.create(data)

    def mark_exit(
        self,
        log_id: UUID,
        exit_time: datetime,
        notes: str | None = None,
    ) -> Optional[VisitorLog]:
        return self.repository.update_exit(
            log_id=log_id,
            exit_time=exit_time,
            notes=notes,
        )

    def get_log(self, log_id: UUID) -> Optional[VisitorLog]:
        return self.repository.get(log_id)

    def list_for_flat(self, flat_id: UUID) -> List[VisitorLog]:
        return self.repository.list_by_flat(flat_id)

    def list_all(self) -> List[VisitorLog]:
        return self.repository.list_all()
