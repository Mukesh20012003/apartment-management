# backend/app/schemas/flat.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class FlatBase(BaseModel):
    flat_number: str
    floor_number: int
    building_section: str
    area_sqft: int
    ownership_type: str

class FlatCreate(FlatBase):
    pass

class FlatResponse(FlatBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
