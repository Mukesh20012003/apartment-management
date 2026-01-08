# backend/app/schemas/visitor.py
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class VisitorLogCreate(BaseModel):
    flat_id: UUID
    visitor_name: str = Field(..., min_length=3)
    visitor_phone: str = Field(..., min_length=10)
    visitor_id_proof: Optional[str] = None
    purpose: str
    vehicle_number: Optional[str] = None
    notes: Optional[str] = None

class VisitorLogExit(BaseModel):
    exit_time: datetime
    notes: Optional[str] = None

class VisitorLogResponse(VisitorLogCreate):
    id: UUID
    security_id: UUID
    entry_time: datetime
    exit_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
