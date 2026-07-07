from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.flight_offer import FlightOffer
    from app.models.watchlist import Watchlist


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    __table_args__ = (
        Index("ix_price_snapshots_watchlist_id", "watchlist_id"),
        Index("ix_price_snapshots_flight_offer_id", "flight_offer_id"),
        Index("ix_price_snapshots_checked_at", "checked_at"),
        Index("ix_price_snapshots_price", "price"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))
    flight_offer_id: Mapped[int] = mapped_column(ForeignKey("flight_offers.id", ondelete="CASCADE"))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    watchlist: Mapped[Watchlist] = relationship(back_populates="price_snapshots")
    flight_offer: Mapped[FlightOffer] = relationship(back_populates="price_snapshots")
