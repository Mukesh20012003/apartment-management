from typing import Annotated,List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.dependencies import get_current_user, require_role
from app.repositories.resident_repository import ResidentRepository
from app.schemas.resident import ResidentCreate, ResidentResponse  # adjust names
from app.core.constants import UserRole, ResidentStatus
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/residents",
    tags=["Residents"],
)

CurrentUser = Annotated[User, Depends(get_current_user)]
AdminOrAssoc = Annotated[
    User,
    Depends(require_role(UserRole.ADMIN, UserRole.ASSOCIATION_STAFF)),
]


@router.post(
    "/",
    response_model=ResidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_resident(
    resident_in: ResidentCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: AdminOrAssoc,
):
    repo = ResidentRepository(db)
    resident = repo.create(
        {
            "user_id": resident_in.user_id,
            "flat_id": resident_in.flat_id,
            "status": ResidentStatus.APPROVED,
            "move_in_date": resident_in.move_in_date,
            "id_proof_url": resident_in.id_proof_url,
            "ownership_proof_url": resident_in.ownership_proof_url,
            "family_members": resident_in.family_members,
            "vehicle_details": resident_in.vehicle_details,
            "emergency_contact": resident_in.emergency_contact,
            "approval_notes": resident_in.approval_notes,
        }
    )
    return resident


@router.get(
    "/",
    response_model=List[ResidentResponse],
)
async def list_residents(
    db: Annotated[Session, Depends(get_db)],
    current_user: AdminOrAssoc,
):
    """
    Get all residents (admin/association staff only).
    """
    repo = ResidentRepository(db)
    # use your BaseRepository list/get_multi method name
    residents = repo.read_all() 
    return residents