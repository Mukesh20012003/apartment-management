from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.repositories.payment_repository import (
    MonthlyFeeRepository,
    PaymentRepository,
)
from app.models.payment import MonthlyFee, Payment
from app.core.constants import PaymentStatus


class PaymentService:
    def __init__(
        self,
        fee_repo: MonthlyFeeRepository,
        payment_repo: PaymentRepository,
    ):
        self.fee_repo = fee_repo
        self.payment_repo = payment_repo

    # Monthly fees

    def list_fees_for_flat(self, flat_id: UUID) -> List[MonthlyFee]:
        return self.fee_repo.list_for_flat(flat_id)

    def list_pending_fees_for_flat(self, flat_id: UUID) -> List[MonthlyFee]:
        return self.fee_repo.list_pending_for_flat(flat_id)

    def create_monthly_fee(self, data: dict) -> MonthlyFee:
        return self.fee_repo.create(data)

    # Payments

    def list_payments_for_resident(self, resident_id: UUID) -> List[Payment]:
        return self.payment_repo.list_for_resident(resident_id)

    def list_all_payments(self) -> List[Payment]:
        return self.payment_repo.list_all()

    def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        return self.payment_repo.get(payment_id)

    def create_payment(
        self,
        *,
        resident_id: UUID,
        fee_id: UUID,
        amount: int,
        payment_method: str,
        transaction_id: str,
        payment_date: str | None = None,
        receipt_url: str | None = None,
        notes: str | None = None,
    ) -> Payment:
        fee = self.fee_repo.get(fee_id)
        if not fee:
            raise ValueError("Monthly fee not found")

        data = {
            "resident_id": resident_id,
            "fee_id": fee_id,
            "amount": amount,
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "status": PaymentStatus.COMPLETED,
            "payment_date": payment_date or datetime.utcnow().isoformat(),
            "receipt_url": receipt_url,
            "notes": notes,
        }
        payment = self.payment_repo.create(data)

        # mark fee as paid
        self.fee_repo.update(fee, {"status": PaymentStatus.COMPLETED})
        return payment
