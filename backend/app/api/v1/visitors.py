from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.visitor_repository import VisitorLogRepository
from app.services.visitor_service import VisitorService
from app.schemas.visitor import VisitorLogCreate, VisitorLogExit, VisitorLogResponse
from app.schemas.user import UserResponse, UserRole
from app.api.dependencies import get_current_user, require_role


router = APIRouter(prefix="/visitors", tags=["visitors"])


def get_visitor_service(db: Session = Depends(get_db)) -> VisitorService:
    repo = VisitorLogRepository(db)
    return VisitorService(repo)


@router.post(
    "/",
    response_model=VisitorLogResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.SECURITY, UserRole.ADMIN))],
)
def create_visitor_entry(
    payload: VisitorLogCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: VisitorService = Depends(get_visitor_service),
):
    visitor_log = service.create_entry(
        flat_id=payload.flat_id,
        security_id=current_user.id,
        visitor_name=payload.visitor_name,
        visitor_phone=payload.visitor_phone,
        visitor_id_proof=payload.visitor_id_proof,
        purpose=payload.purpose,
        vehicle_number=payload.vehicle_number,
        notes=payload.notes,
    )
    return visitor_log


@router.post(
    "/{log_id}/exit",
    response_model=VisitorLogResponse,
    dependencies=[Depends(require_role(UserRole.SECURITY, UserRole.ADMIN))],
)
def mark_visitor_exit(
    log_id: UUID,
    payload: VisitorLogExit,
    service: VisitorService = Depends(get_visitor_service),
):
    visitor_log = service.mark_exit(
        log_id=log_id,
        exit_time=payload.exit_time,
        notes=payload.notes,
    )
    if not visitor_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitor log not found",
        )
    return visitor_log


@router.get(
    "/flat/{flat_id}",
    response_model=List[VisitorLogResponse],
    dependencies=[Depends(require_role(UserRole.SECURITY, UserRole.ADMIN))],
)
def list_visitors_for_flat(
    flat_id: UUID,
    service: VisitorService = Depends(get_visitor_service),
):
    return service.list_for_flat(flat_id)


@router.get(
    "/",
    response_model=List[VisitorLogResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def list_all_visitors(
    service: VisitorService = Depends(get_visitor_service),
):
    return service.list_all()
