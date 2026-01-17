from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.payment import MonthlyFee, Payment
from app.core.constants import PaymentStatus


class MonthlyFeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, fee_id: UUID) -> Optional[MonthlyFee]:
        return self.db.query(MonthlyFee).filter(MonthlyFee.id == fee_id).first()

    def list_for_flat(self, flat_id: UUID) -> List[MonthlyFee]:
        return (
            self.db.query(MonthlyFee)
            .filter(MonthlyFee.flat_id == flat_id)
            .order_by(MonthlyFee.month_year.desc())
            .all()
        )

    def list_pending_for_flat(self, flat_id: UUID) -> List[MonthlyFee]:
        return (
            self.db.query(MonthlyFee)
            .filter(
                MonthlyFee.flat_id == flat_id,
                MonthlyFee.status == PaymentStatus.PENDING,
            )
            .order_by(MonthlyFee.month_year.asc())
            .all()
        )

    def update(self, fee: MonthlyFee, data: dict) -> MonthlyFee:
        for k, v in data.items():
            setattr(fee, k, v)
        self.db.commit()
        self.db.refresh(fee)
        return fee

    def create(self, data: dict) -> MonthlyFee:
        fee = MonthlyFee(**data)
        self.db.add(fee)
        self.db.commit()
        self.db.refresh(fee)
        return fee


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Payment:
        payment = Payment(**data)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get(self, payment_id: UUID) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def list_for_resident(self, resident_id: UUID) -> List[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.resident_id == resident_id)
            .order_by(Payment.payment_date.desc())
            .all()
        )

    def list_all(self) -> List[Payment]:
        return (
            self.db.query(Payment)
            .order_by(Payment.payment_date.desc())
            .all()
        )

    def update(self, payment: Payment, data: dict) -> Payment:
        for k, v in data.items():
            setattr(payment, k, v)
        self.db.commit()
        self.db.refresh(payment)
        return payment
