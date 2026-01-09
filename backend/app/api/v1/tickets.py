# backend/app/api/v1/tickets.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.services.ticket_service import TicketService
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketAssign,
    TicketUpdate,
)
from app.core.constants import UserRole
from app.models.user import User
from app.cache.decorators import cached, invalidate_cache
from app.cache.cache_keys import CacheKeys

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


def get_ticket_service(db: Session) -> TicketService:
    """Helper to build TicketService from DB session."""
    repository = TicketRepository(db)
    return TicketService(repository, db)


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
@invalidate_cache(CacheKeys.open_tickets())
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Create maintenance ticket. Only residents can create.
    """
    if current_user.role != UserRole.RESIDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only residents can create tickets",
        )

    from app.repositories.resident_repository import ResidentRepository

    resident_repo = ResidentRepository(db)
    resident = resident_repo.get_by_user(current_user.id)

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident profile not found",
        )

    service = get_ticket_service(db)

    ticket = service.create_ticket(
        resident_id=resident.id,
        flat_id=resident.flat_id,
        title=ticket_data.title,
        description=ticket_data.description,
        category=ticket_data.category,
        priority=ticket_data.priority,
    )

    return ticket


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
@cached(CacheKeys.ticket_by_id, ttl=1800)
async def get_ticket(
    ticket_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get ticket details by ID.
    """
    service = get_ticket_service(db)

    ticket = service.read(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket


@router.post(
    "/{ticket_id}/assign",
    response_model=TicketResponse,
)
@invalidate_cache(CacheKeys.open_tickets())
async def assign_ticket(
    ticket_id: UUID,
    assign_data: TicketAssign,
    current_user: Annotated[
        User,
        Depends(
            require_role(
                UserRole.ASSOCIATION_STAFF,
                UserRole.ADMIN,
            )
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Assign ticket to staff. Only association staff or admins can assign.
    """
    service = get_ticket_service(db)

    ticket = service.assign_ticket(
        ticket_id=ticket_id,
        assigned_to_id=assign_data.assigned_to_id,
        estimated_cost=assign_data.estimated_cost,
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
)
@invalidate_cache(CacheKeys.ticket_by_id)
async def update_ticket(
    ticket_id: UUID,
    ticket_update: TicketUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Update ticket details (e.g., status, description).
    """
    service = get_ticket_service(db)

    ticket = service.update(
        ticket_id,
        ticket_update.dict(exclude_unset=True),
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket
