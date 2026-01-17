# backend/app/api/v1/flats.py
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.flat import FlatCreate, FlatResponse
from app.repositories.resident_repository import FlatRepository

router = APIRouter(
    prefix="/api/v1/flats",
    tags=["Flats"],
)


def get_flat_repo(db: Session) -> FlatRepository:
    return FlatRepository(db)


@router.post(
    "/",
    response_model=FlatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_flat(
    flat_in: FlatCreate,
    db: Annotated[Session, Depends(get_db)],
):
    repo = get_flat_repo(db)
    flat = repo.create(
        {
            "flat_number": flat_in.flat_number,
            "floor_number": flat_in.floor_number,
            "building_section": flat_in.building_section,
            "area_sqft": flat_in.area_sqft,
            "ownership_type": flat_in.ownership_type,
        }
    )
    return flat


@router.get(
    "/",
    response_model=List[FlatResponse],
)
async def list_flats(
    db: Annotated[Session, Depends(get_db)],
):
    repo = get_flat_repo(db)
    flats = repo.read_all()   # <-- use BaseRepository.read_all
    return flats


@router.get(
    "/{flat_id}",
    response_model=FlatResponse,
)
async def get_flat(
    flat_id: UUID,
    db: Annotated[Session, Depends(get_db)],
):
    repo = get_flat_repo(db)
    flat = repo.read(flat_id)
    if not flat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flat not found",
        )
    return flat
