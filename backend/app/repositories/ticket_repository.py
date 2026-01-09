# backend/app/repositories/ticket_repository.py
from app.repositories.base_repository import BaseRepository
from app.models.ticket import Ticket
from app.core.constants import TicketStatus
from sqlalchemy.orm import Session
from typing import List

class TicketRepository(BaseRepository[Ticket]):
    """Ticket-specific repository"""

    def __init__(self, db: Session):
        super().__init__(Ticket, db)

    def get_by_resident(self, resident_id, skip: int = 0, limit: int = 50) -> List[Ticket]:
        """Get tickets by resident"""
        return self.db.query(self.model).filter(
            self.model.resident_id == resident_id
        ).offset(skip).limit(limit).all()

    def get_by_status(self, status: TicketStatus, skip: int = 0, limit: int = 50) -> List[Ticket]:
        """Get tickets by status"""
        return self.db.query(self.model).filter(
            self.model.status == status
        ).offset(skip).limit(limit).all()

    def get_open_tickets(self, skip: int = 0, limit: int = 50) -> List[Ticket]:
        """Get all open tickets"""
        return self.get_by_status(TicketStatus.OPEN, skip, limit)

    def assign_ticket(self, ticket_id, assigned_to_id, estimated_cost: int = None) -> Ticket:
        """Assign ticket to staff"""
        from datetime import datetime
        return self.update(ticket_id, {
            "assigned_to_id": assigned_to_id,
            "status": TicketStatus.ASSIGNED,
            "assigned_at": datetime.utcnow(),
            "estimated_cost": estimated_cost
        })

    def resolve_ticket(self, ticket_id, resolution_notes: str, actual_cost: int = None) -> Ticket:
        """Mark ticket as resolved"""
        from datetime import datetime
        return self.update(ticket_id, {
            "status": TicketStatus.RESOLVED,
            "resolution_notes": resolution_notes,
            "actual_cost": actual_cost,
            "resolved_at": datetime.utcnow()
        })
