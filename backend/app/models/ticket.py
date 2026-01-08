# backend/app/models/ticket.py
from sqlalchemy import Column, String, Enum, ForeignKey, Text, Integer, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import BaseModel
from app.core.constants import TicketStatus, TicketPriority
from datetime import datetime
import uuid

class Ticket(BaseModel):
    """Maintenance ticket model"""
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    resident_id = Column(UUID(as_uuid=True), ForeignKey("residents.id"), nullable=False, index=True)
    flat_id = Column(UUID(as_uuid=True), ForeignKey("flats.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # Plumbing, Electrical, etc.
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, index=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, index=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    estimated_cost = Column(Integer, nullable=True)
    actual_cost = Column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_ticket_status", "status"),
        Index("idx_ticket_resident", "resident_id"),
        Index("idx_ticket_flat", "flat_id"),
        Index("idx_ticket_assigned", "assigned_to_id"),
    )
