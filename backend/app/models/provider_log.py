from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ProviderLogStatus, ProviderName
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.watchlist import Watchlist


class ProviderLog(TimestampMixin, Base):
    __tablename__ = "provider_logs"
    __table_args__ = (
        Index("ix_provider_logs_provider", "provider"),
        Index("ix_provider_logs_watchlist_id", "watchlist_id"),
        Index("ix_provider_logs_status", "status"),
        Index("ix_provider_logs_created_at", "created_at"),
        Index("ix_provider_logs_request_hash", "request_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[ProviderName] = mapped_column(
        Enum(ProviderName, native_enum=False, length=20),
        nullable=False,
    )
    watchlist_id: Mapped[int | None] = mapped_column(
        ForeignKey("watchlists.id", ondelete="SET NULL"),
        nullable=True,
    )
    request_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[ProviderLogStatus] = mapped_column(
        Enum(ProviderLogStatus, native_enum=False, length=20),
        nullable=False,
    )
    status_code: Mapped[int | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(nullable=True)

    watchlist: Mapped[Watchlist | None] = relationship(back_populates="provider_logs")
