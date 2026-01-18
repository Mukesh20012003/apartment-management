from datetime import datetime
from typing import List, Optional
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from app.services.base_service import BaseService  # assuming you have this
from app.repositories.notice_repository import NoticeRepository
from app.core.constants import NoticeStatus
from app.core.exceptions import AppException  # create if missing
from app.events.events import NoticePublishedEvent  # create if missing

logger = logging.getLogger(__name__)

class NoticeService(BaseService):
    """Production notice service with events"""
    
    def __init__(self, repository: NoticeRepository, db: Session):
        super().__init__(repository, db)
        self.repository = repository
        self.db = db

    def create_notice(
        self,
        title: str,
        content: str,
        published_by_id: UUID,
        category: str,
        attachment_url: Optional[str] = None,
        expiry_date: Optional[str] = None
    ):
        """Create notice (initially as draft)"""
        notice_data = {
            "title": title,
            "content": content,
            "published_by_id": published_by_id,
            "category": category,
            "attachment_url": attachment_url,
            "expiry_date": expiry_date,
            "status": NoticeStatus.DRAFT
        }

        notice = self.repository.create(notice_data)
        logger.info(f"Notice created as draft: {notice.id}")
        return notice

    def publish_notice(self, notice_id: UUID, event_publisher=None):
        """Publish notice and emit event"""
        notice = self.repository.read(notice_id)
        if not notice:
            raise AppException("Notice not found")

        # Update status
        updated = self.repository.update(notice_id, {
            "status": NoticeStatus.PUBLISHED,
            "published_date": datetime.utcnow().isoformat()
        })

        # Emit event (for email/push notifications)
        if event_publisher:
            event = NoticePublishedEvent({
                "notice_id": str(notice_id),
                "title": notice.title,
                "content": notice.content[:100] + "..."
            })
            event_publisher.publish(event)
            
        logger.info(f"Notice published: {notice_id}")
        return updated

    def archive_notice(self, notice_id: UUID):
        """Archive notice (hide from residents)"""
        return self.repository.update(notice_id, {
            "status": NoticeStatus.ARCHIVED
        })

    def list_active_notices(self, skip: int = 0, limit: int = 50) -> List:
        """Get published/active notices with pagination"""
        return self.repository.list_active(skip=skip, limit=limit)

    def get_notice(self, notice_id: UUID):
        """Get single notice"""
        return self.repository.read(notice_id)
