# backend/app/models/visitor.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import BaseModel
import uuid

class VisitorLog(BaseModel):
    """Visitor entry/exit log"""
    __tablename__ = "visitor_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flat_id = Column(UUID(as_uuid=True), ForeignKey("flats.id"), nullable=False, index=True)
    security_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    visitor_name = Column(String(255), nullable=False)
    visitor_phone = Column(String(20), nullable=False)
    visitor_id_proof = Column(String(50), nullable=True)
    purpose = Column(String(255), nullable=False)
    entry_time = Column(DateTime, nullable=False, index=True)
    exit_time = Column(DateTime, nullable=True)
    vehicle_number = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_visitor_flat", "flat_id"),
        Index("idx_visitor_entry_exit", "entry_time", "exit_time"),
    )
