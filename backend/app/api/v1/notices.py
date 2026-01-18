from typing import List
from uuid import UUID


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.database.session import get_db
from app.repositories.notice_repository import NoticeRepository
from app.services.notice_service import NoticeService
from app.schemas.notice import (  # you create these Pydantic models
    NoticeCreate,
    NoticeUpdate,
    NoticeResponse,
)


from app.schemas.user import UserResponse, UserRole
from app.api.dependencies import get_current_user, require_role
from app.core.constants import NoticeStatus, UserRole


router = APIRouter(prefix="/notices", tags=["notices"])



def get_notice_service(db: Session = Depends(get_db)) -> NoticeService:
    repo = NoticeRepository(db)
    return NoticeService(repo)



# Admin/association users manage notices
admin_roles = (UserRole.ADMIN, UserRole.ASSOCIATION_STAFF)



@router.post(
    "/",
    response_model=NoticeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*admin_roles))],
)
def create_notice(
    payload: NoticeCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: NoticeService = Depends(get_notice_service),
):
    notice = service.create_notice(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        published_by_id=current_user.id,
        attachment_url=payload.attachment_url,
        status=payload.status or NoticeStatus.DRAFT,
        published_date=payload.published_date,
        expiry_date=payload.expiry_date,
    )
    return notice



@router.post(
    "/{notice_id}/publish",
    response_model=NoticeResponse,
    dependencies=[Depends(require_role(*admin_roles))],
)
def publish_notice(
    notice_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: NoticeService = Depends(get_notice_service),
):
    notice = service.publish_notice(
        notice_id=notice_id,
        published_by_id=current_user.id,
    )
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found",
        )
    return notice



@router.patch(
    "/{notice_id}",
    response_model=NoticeResponse,
    dependencies=[Depends(require_role(*admin_roles))],
)
def update_notice(
    notice_id: UUID,
    payload: NoticeUpdate,
    service: NoticeService = Depends(get_notice_service),
):
    notice = service.update_notice(
        notice_id=notice_id,
        data=payload.model_dump(exclude_unset=True),
    )
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found",
        )
    return notice



@router.delete(
    "/{notice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(*admin_roles))],
)
def delete_notice(
    notice_id: UUID,
    service: NoticeService = Depends(get_notice_service),
):
    ok = service.delete_notice(notice_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found",
        )
    return



# Public/resident endpoints



@router.get(
    "/",
    response_model=List[NoticeResponse],
)
def list_active_notices(
    service: NoticeService = Depends(get_notice_service),
):
    """All logged-in users can see active notices (or keep fully public if your auth allows)."""
    return service.list_active_notices()



@router.get(
    "/{notice_id}",
    response_model=NoticeResponse,
)
def get_notice(
    notice_id: UUID,
    service: NoticeService = Depends(get_notice_service),
):
    notice = service.get_notice(notice_id)
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found",
        )
    return notice