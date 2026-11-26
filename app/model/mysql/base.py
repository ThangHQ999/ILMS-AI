from datetime import datetime
from typing import Any
import uuid
from sqlalchemy import BINARY, DateTime, TypeDecorator, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Lớp cơ sở cho tất cả SQLAlchemy ORM models trong MySQL."""
    pass


class TimestampMixin:
    """Mixin tự động gắn thời gian khởi tạo (created_at) và cập nhật (updated_at)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
class BinaryUUID(TypeDecorator):
    """
    TypeDecorator tự động convert giữa String UUID (Python) và BINARY(16) (MySQL).
    """
    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: Any) -> bytes | None:
        if value is None:
            return None
        return uuid.UUID(value).bytes

    def process_result_value(self, value: bytes | None, dialect: Any) -> str | None:
        if value is None:
            return None
        return str(uuid.UUID(bytes=value))