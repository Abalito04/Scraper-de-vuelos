from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.watchlist import Watchlist


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    preferred_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    watchlists: Mapped[list[Watchlist]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
