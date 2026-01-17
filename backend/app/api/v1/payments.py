from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.payment_repository import (
    MonthlyFeeRepository,
    PaymentRepository,
)
from app.services.payment_service import PaymentService
from app.schemas.payment import (
    MonthlyFeeCreate,
    MonthlyFeeResponse,
    PaymentCreate,
    PaymentResponse,
)
from app.schemas.user import UserResponse, UserRole
from app.api.dependencies import get_current_user, require_role
from app.models.resident import Resident

router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    fee_repo = MonthlyFeeRepository(db)
    payment_repo = PaymentRepository(db)
    return PaymentService(fee_repo, payment_repo)


resident_roles = (UserRole.RESIDENT,)
admin_roles = (UserRole.ADMIN, UserRole.ASSOCIATION_STAFF)


# Admin: create monthly fee records for flats

@router.post(
    "/fees/",
    response_model=MonthlyFeeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*admin_roles))],
)
def create_monthly_fee(
    payload: MonthlyFeeCreate,
    service: PaymentService = Depends(get_payment_service),
):
    fee = service.create_monthly_fee(payload.model_dump())
    return fee


@router.get(
    "/fees/flat/{flat_id}",
    response_model=List[MonthlyFeeResponse],
    dependencies=[Depends(require_role(*admin_roles))],
)
def list_fees_for_flat(
    flat_id: UUID,
    service: PaymentService = Depends(get_payment_service),
):
    return service.list_fees_for_flat(flat_id)


# Resident: view own pending fees and payment history

@router.get(
    "/fees/pending",
    response_model=List[MonthlyFeeResponse],
    dependencies=[Depends(require_role(*resident_roles))],
)
def list_my_pending_fees(
    current_user: UserResponse = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
    db: Session = Depends(get_db),
):
    # find resident linked to this user
    resident = (
        db.query(Resident)
        .filter(Resident.user_id == current_user.id)
        .first()
    )
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident profile not found for current user",
        )

    return service.list_pending_fees_for_flat(resident.flat_id)


@router.get(
    "/my",
    response_model=List[PaymentResponse],
    dependencies=[Depends(require_role(*resident_roles))],
)
def list_my_payments(
    current_user: UserResponse = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
    db: Session = Depends(get_db),
):
    resident = (
        db.query(Resident)
        .filter(Resident.user_id == current_user.id)
        .first()
    )
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident profile not found for current user",
        )

    return service.list_payments_for_resident(resident.id)



# Resident: create a payment against a fee

@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*resident_roles))],
)
def create_payment(
    payload: PaymentCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
    db: Session = Depends(get_db),
):
    # Resolve resident linked to this user
    resident = (
        db.query(Resident)
        .filter(Resident.user_id == current_user.id)
        .first()
    )
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident profile not found for current user",
        )

    try:
        payment = service.create_payment(
            resident_id=resident.id,
            fee_id=payload.fee_id,
            amount=payload.amount,
            payment_method=payload.payment_method,
            transaction_id=payload.transaction_id,
            payment_date=payload.payment_date,
            receipt_url=payload.receipt_url,
            notes=payload.notes,
        )
        return payment
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monthly fee not found",
        )



# Admin: list all payments

@router.get(
    "/",
    response_model=List[PaymentResponse],
    dependencies=[Depends(require_role(*admin_roles))],
)
def list_all_payments(
    service: PaymentService = Depends(get_payment_service),
):
    return service.list_all_payments()
