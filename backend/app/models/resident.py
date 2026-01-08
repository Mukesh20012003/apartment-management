# backend/app/models/resident.py
from sqlalchemy import Column, String, Enum, ForeignKey, Integer, Boolean, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import BaseModel
from app.core.constants import ResidentStatus
import uuid

class Flat(BaseModel):
    """Flat/Apartment model"""
    __tablename__ = "flats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flat_number = Column(String(20), unique=True, nullable=False, index=True)
    floor_number = Column(Integer, nullable=False)
    building_section = Column(String(50), nullable=False)
    area_sqft = Column(Integer, nullable=False)
    ownership_type = Column(String(50), nullable=False)  # Owned/Rented

class Resident(BaseModel):
    """Resident model"""
    __tablename__ = "residents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    flat_id = Column(UUID(as_uuid=True), ForeignKey("flats.id"), nullable=False, index=True)
    status = Column(Enum(ResidentStatus), default=ResidentStatus.PENDING, index=True)
    move_in_date = Column(String(50), nullable=True)
    id_proof_url = Column(String(255), nullable=True)
    ownership_proof_url = Column(String(255), nullable=True)
    family_members = Column(Integer, default=1)
    vehicle_details = Column(Text, nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    approval_notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_resident_status", "status"),
        Index("idx_resident_user_flat", "user_id", "flat_id"),
    )
