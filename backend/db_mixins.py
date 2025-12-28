import datetime
from enum import Enum

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class BaseSQLModel(DeclarativeBase):
    pass


class DBUserTypeEnum(str, Enum):
    admin = 'admin'
    script = 'script'
    user = 'user'


class HistoricalMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_by: Mapped[DBUserTypeEnum] = mapped_column(String(64))
    