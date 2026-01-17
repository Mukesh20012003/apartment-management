# backend/app/schemas/resident.py
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.core.constants import ResidentStatus
from datetime import datetime

class FlatBase(BaseModel):
    flat_number: str
    floor_number: int
    building_section: str
    area_sqft: int
    ownership_type: str

class FlatResponse(FlatBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResidentBase(BaseModel):
    user_id: UUID
    flat_id: UUID
    status: ResidentStatus = ResidentStatus.APPROVED
    move_in_date: Optional[datetime] = None
    id_proof_url: Optional[str] = None
    ownership_proof_url: Optional[str] = None
    family_members: int = 1 
    vehicle_details: Optional[str] = None
    emergency_contact: Optional[str] = None
    approval_notes: Optional[str] = None

class ResidentCreate(ResidentBase):
    pass

class ResidentRegister(ResidentBase):
    user_id: UUID

class ResidentResponse(ResidentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResidentApproval(BaseModel):
    status: ResidentStatus = ResidentStatus.APPROVED
    approval_notes: Optional[str] = None
