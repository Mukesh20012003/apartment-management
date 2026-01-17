# backend/app/services/ticket_service.py
from typing import Optional
from uuid import UUID
import logging
import uuid

from sqlalchemy.orm import Session

from app.services.base_service import BaseService
from app.repositories.ticket_repository import TicketRepository
from app.core.constants import TicketStatus, TicketPriority
from app.core.exceptions import AppException
from app.events.event_bus import publish_event_sync, EventType
from app.cache.redis_cache import get_cache  # sync RedisCache factory


logger = logging.getLogger(__name__)


class TicketService(BaseService):
    """Ticket service"""

    def __init__(self, repository: TicketRepository, db: Session):
        super().__init__(repository, db)
        self.repository = repository
        self.cache = get_cache()

    # ---------- cache key helper ----------

    def _ticket_cache_key(self, ticket_id: UUID) -> str:
        return f"ticket:{ticket_id}"

    # ---------- core methods ----------

    def create_ticket(
        self,
        resident_id: UUID,
        flat_id: UUID,
        title: str,
        description: str,
        category: str,
        priority: TicketPriority = TicketPriority.MEDIUM,
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
            "status": TicketStatus.OPEN,
        }

        ticket = self.repository.create(ticket_data)

        logger.info("Ticket created: %s", ticket.ticket_number)

        # Publish ticket.created event via sync helper
        publish_event_sync(
            EventType.TICKET_CREATED.value,
            {
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "resident_id": str(ticket.resident_id),
                "flat_id": str(ticket.flat_id),
                "created_at": str(ticket.created_at),
            },
        )

        # Invalidate cache just in case (not strictly needed for new id)
        self.cache.delete(self._ticket_cache_key(ticket.id))

        return ticket

    def get_ticket(self, ticket_id: UUID):
        """
        Get single ticket with Redis cache.
        Logs HIT/MISS and caches DB result for 5 minutes.
        """
        key = self._ticket_cache_key(ticket_id)

        cached = self.cache.get(key)
        if cached:
            logger.info("Ticket cache HIT: %s", ticket_id)
            return cached  # assuming RedisCache returns deserialized object

        logger.info("Ticket cache MISS: %s", ticket_id)
        ticket = self.repository.read(ticket_id)
        if not ticket:
            return None

        # Store in cache with TTL (seconds). Adjust serialization if needed.
        self.cache.set(key, ticket, ttl=300)
        logger.info("Ticket cached: %s", ticket_id)
        return ticket

    def get_resident_tickets(
        self,
        resident_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ):
        """Get tickets for resident"""
        return self.repository.get_by_resident(resident_id, skip, limit)

    def assign_ticket(
        self,
        ticket_id: UUID,
        assigned_to_id: UUID,
        estimated_cost: Optional[int] = None,
    ):
        """Assign ticket to staff member"""
        ticket = self.repository.read(ticket_id)
        if not ticket:
            raise AppException("Ticket not found")

        updated = self.repository.assign_ticket(
            ticket_id,
            assigned_to_id,
            estimated_cost,
        )

        # Invalidate cache so subsequent GET sees updated data
        self.cache.delete(self._ticket_cache_key(ticket_id))
        logger.info(
            "Ticket assigned and cache invalidated: %s -> %s",
            ticket_id,
            assigned_to_id,
        )

        return updated

    def resolve_ticket(
        self,
        ticket_id: UUID,
        resolution_notes: str,
        actual_cost: Optional[int] = None,
    ):
        """Mark ticket as resolved"""
        ticket = self.repository.read(ticket_id)
        if not ticket:
            raise AppException("Ticket not found")

        updated = self.repository.resolve_ticket(
            ticket_id,
            resolution_notes,
            actual_cost,
        )

        # Invalidate cache so resolved status is visible
        self.cache.delete(self._ticket_cache_key(ticket_id))
        logger.info("Ticket resolved and cache invalidated: %s", ticket_id)

        return updated

    def get_open_tickets(self, skip: int = 0, limit: int = 50):
        """Get all open tickets"""
        return self.repository.get_open_tickets(skip, limit)
