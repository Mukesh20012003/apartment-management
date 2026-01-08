# backend/app/models/payment.py
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import BaseModel
from app.core.constants import PaymentStatus
import uuid

class MonthlyFee(BaseModel):
    """Monthly fee structure"""
    __tablename__ = "monthly_fees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flat_id = Column(UUID(as_uuid=True), ForeignKey("flats.id"), nullable=False, index=True)
    month_year = Column(String(10), nullable=False)  # MM-YYYY format
    base_amount = Column(Integer, nullable=False)
    maintenance_charge = Column(Integer, default=0)
    water_charge = Column(Integer, default=0)
    other_charges = Column(Integer, default=0)
    penalty_amount = Column(Integer, default=0)
    due_date = Column(String(50), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, index=True)

class Payment(BaseModel):
    """Payment transaction model"""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resident_id = Column(UUID(as_uuid=True), ForeignKey("residents.id"), nullable=False, index=True)
    fee_id = Column(UUID(as_uuid=True), ForeignKey("monthly_fees.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    payment_method = Column(String(50), nullable=False)  # Card, UPI, Bank Transfer, etc.
    transaction_id = Column(String(255), unique=True, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    payment_date = Column(String(50), nullable=False)
    receipt_url = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_payment_resident", "resident_id"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_transaction", "transaction_id"),
    )
