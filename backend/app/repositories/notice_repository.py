from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notice import Notice
from app.core.constants import NoticeStatus


class NoticeRepository:
    """Data access layer for notices"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Notice:
        notice = Notice(**data)
        self.db.add(notice)
        self.db.commit()
        self.db.refresh(notice)
        return notice

    def get(self, notice_id: UUID) -> Optional[Notice]:
        return (
            self.db.query(Notice)
            .filter(Notice.id == notice_id)
            .first()
        )

    def list_active(self) -> List[Notice]:
        return (
            self.db.query(Notice)
            .filter(Notice.status == NoticeStatus.PUBLISHED)
            .order_by(Notice.created_at.desc())
            .all()
        )

    def list_all(self) -> List[Notice]:
        return (
            self.db.query(Notice)
            .order_by(Notice.created_at.desc())
            .all()
        )

    def update(self, notice: Notice, data: dict) -> Notice:
        for key, value in data.items():
            setattr(notice, key, value)
        self.db.commit()
        self.db.refresh(notice)
        return notice

    def delete(self, notice: Notice) -> None:
        self.db.delete(notice)
        self.db.commit()
