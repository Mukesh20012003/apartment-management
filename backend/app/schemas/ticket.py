# backend/app/schemas/ticket.py
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.core.constants import TicketStatus, TicketPriority
from datetime import datetime

class TicketCreate(BaseModel):
    title: str = Field(..., min_length=10, max_length=255)
    description: str = Field(..., min_length=20)
    category: str
    priority: TicketPriority = TicketPriority.MEDIUM

class TicketResponse(TicketCreate):
    id: UUID
    ticket_number: str
    resident_id: UUID
    flat_id: UUID
    status: TicketStatus
    assigned_to_id: Optional[UUID]
    assigned_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    estimated_cost: Optional[int]
    actual_cost: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketAssign(BaseModel):
    assigned_to_id: UUID
    estimated_cost: Optional[int] = None

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    resolution_notes: Optional[str] = None
    actual_cost: Optional[int] = None
