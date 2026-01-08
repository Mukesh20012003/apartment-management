# backend/app/models/notice.py
from sqlalchemy import Column, String, Enum, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import BaseModel
from app.core.constants import NoticeStatus
import uuid

class Notice(BaseModel):
    """Notice board model"""
    __tablename__ = "notices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    published_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(NoticeStatus), default=NoticeStatus.DRAFT, index=True)
    published_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    category = Column(String(50), nullable=False)  # Maintenance, Event, Announcement, etc.
    attachment_url = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_notice_status", "status"),
        Index("idx_notice_published_by", "published_by_id"),
    )
