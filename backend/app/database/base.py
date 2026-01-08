# backend/app/database/base.py
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base, declared_attr

Base = declarative_base()


class BaseModel(Base):
    """Base model with common columns."""
    __abstract__ = True
    __allow_unmapped__ = True  # allow legacy style without Mapped[]

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Import models so Alembic sees them
from app.models.user import User  # noqa
from app.models.resident import Flat, Resident  # noqa
from app.models.ticket import Ticket  # noqa
from app.models.visitor import VisitorLog  # noqa
from app.models.payment import MonthlyFee, Payment  # noqa
from app.models.notice import Notice  # noqa
