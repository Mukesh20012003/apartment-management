# backend/app/schemas/notice.py
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from app.core.constants import NoticeStatus


class NoticeBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    category: str
    attachment_url: Optional[str] = None
    status: Optional[NoticeStatus] = None
    published_date: Optional[str] = None
    expiry_date: Optional[str] = None


class NoticeCreate(NoticeBase):
    pass


class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    attachment_url: Optional[str] = None
    status: Optional[NoticeStatus] = None
    published_date: Optional[str] = None
    expiry_date: Optional[str] = None


class NoticeResponse(NoticeBase):
    id: UUID
    published_by_id: UUID

    class Config:
        from_attributes = True
