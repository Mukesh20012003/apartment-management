from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID
import uuid
import logging

from app.repositories.payment_repository import MonthlyFeeRepository, PaymentRepository
from app.core.constants import PaymentStatus

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, fee_repo: MonthlyFeeRepository, payment_repo: PaymentRepository):
        self.fee_repo = fee_repo
        self.payment_repo = payment_repo

    # ✅ YOUR EXISTING METHODS (keep all)
    def list_fees_for_flat(self, flat_id: UUID) -> List:
        return self.fee_repo.list_for_flat(flat_id)

    def list_pending_fees_for_flat(self, flat_id: UUID) -> List:
        return self.fee_repo.list_pending_for_flat(flat_id)

    def create_monthly_fee(self, data: dict):
        return self.fee_repo.create(data)

    def list_payments_for_resident(self, resident_id: UUID) -> List:
        return self.payment_repo.list_for_resident(resident_id)

    def list_all_payments(self) -> List:
        return self.payment_repo.list_all()

    def get_payment(self, payment_id: UUID):
        return self.payment_repo.get(payment_id)

    # ✅ YOUR create_payment (enhanced with Phase 12)
    def create_payment(
        self,
        resident_id: UUID,
        fee_id: UUID,
        amount: int,
        payment_method: str,
        transaction_id: str,
        payment_date: Optional[str] = None,
        receipt_url: Optional[str] = None,
        notes: Optional[str] = None,
    ):
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

        # Mark fee as paid
        self.fee_repo.update(fee, {"status": PaymentStatus.COMPLETED})
        logger.info(f"Payment completed: {transaction_id}")
        return payment

    # 🔥 PHASE 12 NEW FEATURES
    def initiate_payment(self, resident_id: UUID, fee_id: UUID, amount: int, payment_method: str):
        """Phase 12: Initiate gateway payment"""
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        data = {
            "resident_id": resident_id,
            "fee_id": fee_id,
            "amount": amount,
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "status": PaymentStatus.PENDING,
            "payment_date": datetime.utcnow().isoformat()
        }
        payment = self.payment_repo.create(data)
        logger.info(f"Payment initiated: {transaction_id}")
        return payment

    def process_payment_callback(self, transaction_id: str, callback_data: dict):
        """Phase 12: Handle gateway webhook"""
        payment = self.payment_repo.get_by_transaction_id(transaction_id)
        if not payment:
            raise ValueError("Payment not found")

        if callback_data.get("status") == "success":
            data = {
                "status": PaymentStatus.COMPLETED,
                "receipt_url": callback_data.get("receipt_url")
            }
            self.payment_repo.update(payment, data)
            
            # Update fee
            fee = self.fee_repo.get(payment.fee_id)
            if fee:
                self.fee_repo.update(fee, {"status": PaymentStatus.COMPLETED})
            
            logger.info(f"Payment completed: {transaction_id}")
        else:
            data = {
                "status": PaymentStatus.FAILED,
                "notes": callback_data.get("error_message", "Payment failed")
            }
            self.payment_repo.update(payment, data)
            logger.error(f"Payment failed: {transaction_id}")

    def generate_receipt(self, payment_id: UUID) -> dict:
        """Phase 12: Generate receipt"""
        payment = self.payment_repo.get(payment_id)
        if not payment or payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Valid completed payment required")
        
        return {
            "receipt_number": f"RCP-{uuid.uuid4().hex[:8].upper()}",
            "transaction_id": payment.transaction_id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "payment_method": payment.payment_method
        }
