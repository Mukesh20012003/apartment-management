from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.repositories.notice_repository import NoticeRepository
from app.models.notice import Notice
from app.core.constants import NoticeStatus


class NoticeService:
    """Business logic for notice board"""

    def __init__(self, repository: NoticeRepository):
        self.repository = repository

    def create_notice(
        self,
        *,
        title: str,
        content: str,
        category: str,
        published_by_id: UUID,
        attachment_url: str | None = None,
        status: NoticeStatus = NoticeStatus.DRAFT,
        published_date: str | None = None,
        expiry_date: str | None = None,
    ) -> Notice:
        data = {
            "title": title,
            "content": content,
            "category": category,
            "published_by_id": published_by_id,
            "attachment_url": attachment_url,
            "status": status,
            "published_date": published_date,
            "expiry_date": expiry_date,
        }
        return self.repository.create(data)

    def publish_notice(
        self,
        notice_id: UUID,
        published_by_id: UUID,
        published_date: str | None = None,
        expiry_date: str | None = None,
    ) -> Optional[Notice]:
        notice = self.repository.get(notice_id)
        if not notice:
            return None

        data = {
            "status": NoticeStatus.PUBLISHED,
            "published_date": published_date or datetime.utcnow().isoformat(),
            "expiry_date": expiry_date,
            "published_by_id": published_by_id,
        }
        return self.repository.update(notice, data)

    def update_notice(
        self,
        notice_id: UUID,
        data: dict,
    ) -> Optional[Notice]:
        notice = self.repository.get(notice_id)
        if not notice:
            return None
        return self.repository.update(notice, data)

    def delete_notice(self, notice_id: UUID) -> bool:
        notice = self.repository.get(notice_id)
        if not notice:
            return False
        self.repository.delete(notice)
        return True

    def get_notice(self, notice_id: UUID) -> Optional[Notice]:
        return self.repository.get(notice_id)

    def list_active_notices(self) -> List[Notice]:
        return self.repository.list_active()

    def list_all_notices(self) -> List[Notice]:
        return self.repository.list_all()
