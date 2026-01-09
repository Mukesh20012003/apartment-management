# backend/app/services/ticket_service.py
from app.services.base_service import BaseService
from app.repositories.ticket_repository import TicketRepository
from app.core.constants import TicketStatus, TicketPriority
from app.core.exceptions import AppException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging
import uuid

logger = logging.getLogger(__name__)

class TicketService(BaseService):
    """Ticket service"""
    
    def __init__(self, repository: TicketRepository, db: Session):
        super().__init__(repository, db)
        self.repository = repository

    def create_ticket(
        self,
        resident_id: UUID,
        flat_id: UUID,
        title: str,
        description: str,
        category: str,
        priority: TicketPriority = TicketPriority.MEDIUM
    ):
        """Create maintenance ticket"""
        ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"

        ticket_data = {
            "ticket_number": ticket_number,
            "resident_id": resident_id,
            "flat_id": flat_id,
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "status": TicketStatus.OPEN
        }

        ticket = self.repository.create(ticket_data)
        
        # Emit event for ticket creation notification
        logger.info(f"Ticket created: {ticket.ticket_number}")
        
        return ticket

    def get_resident_tickets(self, resident_id: UUID, skip: int = 0, limit: int = 50):
        """Get tickets for resident"""
        return self.repository.get_by_resident(resident_id, skip, limit)

    def assign_ticket(self, ticket_id: UUID, assigned_to_id: UUID, estimated_cost: int = None):
        """Assign ticket to staff member"""
        ticket = self.repository.read(ticket_id)
        if not ticket:
            raise AppException("Ticket not found")

        updated = self.repository.assign_ticket(ticket_id, assigned_to_id, estimated_cost)
        
        # Emit event for assignment notification
        logger.info(f"Ticket assigned: {ticket_id} to {assigned_to_id}")
        
        return updated

    def resolve_ticket(self, ticket_id: UUID, resolution_notes: str, actual_cost: int = None):
        """Mark ticket as resolved"""
        ticket = self.repository.read(ticket_id)
        if not ticket:
            raise AppException("Ticket not found")

        updated = self.repository.resolve_ticket(ticket_id, resolution_notes, actual_cost)
        
        # Emit event for resolution notification
        logger.info(f"Ticket resolved: {ticket_id}")
        
        return updated

    def get_open_tickets(self, skip: int = 0, limit: int = 50):
        """Get all open tickets"""
        return self.repository.get_open_tickets(skip, limit)
