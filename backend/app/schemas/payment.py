# backend/app/schemas/payment.py
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.constants import PaymentStatus


class MonthlyFeeBase(BaseModel):
    flat_id: UUID
    month_year: str = Field(..., max_length=10)
    base_amount: int
    maintenance_charge: int = 0
    water_charge: int = 0
    other_charges: int = 0
    penalty_amount: int = 0
    due_date: str
    status: PaymentStatus = PaymentStatus.PENDING


class MonthlyFeeCreate(MonthlyFeeBase):
    pass


class MonthlyFeeResponse(MonthlyFeeBase):
    id: UUID

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    fee_id: UUID
    amount: int
    payment_method: str
    transaction_id: str
    payment_date: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    resident_id: UUID
    fee_id: UUID
    amount: int
    payment_method: str
    transaction_id: str
    status: PaymentStatus
    payment_date: str
    receipt_url: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True
