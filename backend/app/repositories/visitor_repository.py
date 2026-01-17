# backend/app/repositories/visitor_repository.py
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.visitor import VisitorLog


class VisitorLogRepository:
    """Data access layer for visitor_logs"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> VisitorLog:
        visitor_log = VisitorLog(**data)
        self.db.add(visitor_log)
        self.db.commit()
        self.db.refresh(visitor_log)
        return visitor_log

    def get(self, log_id: UUID) -> Optional[VisitorLog]:
        return (
            self.db.query(VisitorLog)
            .filter(VisitorLog.id == log_id)
            .first()
        )

    def list_by_flat(self, flat_id: UUID) -> List[VisitorLog]:
        return (
            self.db.query(VisitorLog)
            .filter(VisitorLog.flat_id == flat_id)
            .order_by(VisitorLog.entry_time.desc())
            .all()
        )

    def list_all(self) -> List[VisitorLog]:
        return (
            self.db.query(VisitorLog)
            .order_by(VisitorLog.entry_time.desc())
            .all()
        )

    def update_exit(
        self,
        log_id: UUID,
        exit_time,
        notes: str | None = None,
    ) -> Optional[VisitorLog]:
        visitor_log = self.get(log_id)
        if not visitor_log:
            return None
        visitor_log.exit_time = exit_time
        if notes is not None:
            visitor_log.notes = notes
        self.db.commit()
        self.db.refresh(visitor_log)
        return visitor_log
