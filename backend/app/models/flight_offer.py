from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ProviderName, TripType
from app.db.base import Base, TimestampMixin, utc_now
from app.db.types import json_payload_type

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.price_snapshot import PriceSnapshot
    from app.models.watchlist import Watchlist


class FlightOffer(TimestampMixin, Base):
    __tablename__ = "flight_offers"
    __table_args__ = (
        Index("ix_flight_offers_watchlist_id", "watchlist_id"),
        Index("ix_flight_offers_provider", "provider"),
        Index("ix_flight_offers_origin_code", "origin_code"),
        Index("ix_flight_offers_destination_code", "destination_code"),
        Index("ix_flight_offers_departure_date", "departure_date"),
        Index("ix_flight_offers_return_date", "return_date"),
        Index("ix_flight_offers_total_price", "total_price"),
        Index("ix_flight_offers_found_at", "found_at"),
        Index(
            "uq_flight_offer_dedupe",
            "watchlist_id",
            "provider",
            "origin_code",
            "destination_code",
            "departure_date",
            "return_date",
            "total_price",
            "airline_codes",
            "stops",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))
    provider: Mapped[ProviderName] = mapped_column(
        Enum(ProviderName, native_enum=False, length=20),
        nullable=False,
    )
    provider_offer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origin_code: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_code: Mapped[str] = mapped_column(String(3), nullable=False)
    trip_type: Mapped[TripType] = mapped_column(
        Enum(TripType, native_enum=False, length=20),
        nullable=False,
    )
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    airline_codes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stops: Mapped[int] = mapped_column(nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    deep_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(json_payload_type(), nullable=True)
    found_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    watchlist: Mapped[Watchlist] = relationship(back_populates="flight_offers")
    price_snapshots: Mapped[list[PriceSnapshot]] = relationship(back_populates="flight_offer")
    alerts: Mapped[list[Alert]] = relationship(back_populates="flight_offer")
