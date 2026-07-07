from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CabinClass, TripType
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.flight_offer import FlightOffer
    from app.models.price_snapshot import PriceSnapshot
    from app.models.provider_log import ProviderLog
    from app.models.user import User


class Watchlist(TimestampMixin, Base):
    __tablename__ = "watchlists"
    __table_args__ = (
        CheckConstraint("max_price IS NULL OR max_price > 0", name="max_price_positive"),
        CheckConstraint("max_stops >= 0", name="max_stops_non_negative"),
        CheckConstraint(
            "max_duration_minutes IS NULL OR max_duration_minutes > 0", name="duration_positive"
        ),
        CheckConstraint("adults >= 1", name="adults_positive"),
        CheckConstraint("check_frequency_hours >= 1", name="check_frequency_positive"),
        CheckConstraint(
            "alert_below_average_percent IS NULL OR alert_below_average_percent > 0",
            name="alert_average_percent_positive",
        ),
        CheckConstraint("alert_cooldown_hours >= 0", name="alert_cooldown_non_negative"),
        Index("ix_watchlists_user_id", "user_id"),
        Index("ix_watchlists_active", "active"),
        Index("ix_watchlists_trip_type", "trip_type"),
        Index("ix_watchlists_last_checked_at", "last_checked_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    trip_type: Mapped[TripType] = mapped_column(
        Enum(TripType, native_enum=False, length=20),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    max_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    max_stops: Mapped[int] = mapped_column(default=2, nullable=False)
    max_duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    cabin_class: Mapped[CabinClass] = mapped_column(
        Enum(CabinClass, native_enum=False, length=24),
        default=CabinClass.ECONOMY,
        nullable=False,
    )
    adults: Mapped[int] = mapped_column(default=1, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    check_frequency_hours: Mapped[int] = mapped_column(default=12, nullable=False)
    alert_below_max_price: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alert_below_average_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    alert_on_new_minimum: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alert_cooldown_hours: Mapped[int] = mapped_column(default=24, nullable=False)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="watchlists")
    origins: Mapped[list[WatchlistOrigin]] = relationship(
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )
    destinations: Mapped[list[WatchlistDestination]] = relationship(
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )
    date_windows: Mapped[list[WatchlistDateWindow]] = relationship(
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )
    segments: Mapped[list[WatchlistSegment]] = relationship(
        back_populates="watchlist",
        cascade="all, delete-orphan",
        order_by="WatchlistSegment.segment_order",
    )
    flight_offers: Mapped[list[FlightOffer]] = relationship(back_populates="watchlist")
    price_snapshots: Mapped[list[PriceSnapshot]] = relationship(back_populates="watchlist")
    alerts: Mapped[list[Alert]] = relationship(back_populates="watchlist")
    provider_logs: Mapped[list[ProviderLog]] = relationship(back_populates="watchlist")


class WatchlistOrigin(TimestampMixin, Base):
    __tablename__ = "watchlist_origins"
    __table_args__ = (
        CheckConstraint("length(origin_code) = 3", name="origin_code_iata_length"),
        Index("ix_watchlist_origins_watchlist_id", "watchlist_id"),
        Index("ix_watchlist_origins_origin_code", "origin_code"),
        Index(
            "uq_watchlist_origins_watchlist_id_origin_code",
            "watchlist_id",
            "origin_code",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))
    origin_code: Mapped[str] = mapped_column(String(3), nullable=False)

    watchlist: Mapped[Watchlist] = relationship(back_populates="origins")


class WatchlistDestination(TimestampMixin, Base):
    __tablename__ = "watchlist_destinations"
    __table_args__ = (
        CheckConstraint("length(destination_code) = 3", name="destination_code_iata_length"),
        Index("ix_watchlist_destinations_watchlist_id", "watchlist_id"),
        Index("ix_watchlist_destinations_destination_code", "destination_code"),
        Index(
            "uq_watchlist_destinations_watchlist_id_destination_code",
            "watchlist_id",
            "destination_code",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))
    destination_code: Mapped[str] = mapped_column(String(3), nullable=False)

    watchlist: Mapped[Watchlist] = relationship(back_populates="destinations")


class WatchlistDateWindow(TimestampMixin, Base):
    __tablename__ = "watchlist_date_windows"
    __table_args__ = (
        CheckConstraint("departure_date_from <= departure_date_to", name="departure_window_order"),
        CheckConstraint(
            "return_date_from IS NULL OR return_date_to IS NULL OR return_date_from <= return_date_to",
            name="return_window_order",
        ),
        CheckConstraint(
            "min_trip_days IS NULL OR max_trip_days IS NULL OR min_trip_days <= max_trip_days",
            name="trip_days_order",
        ),
        Index("ix_watchlist_date_windows_watchlist_id", "watchlist_id"),
        Index("ix_watchlist_date_windows_departure_date_from", "departure_date_from"),
        Index("ix_watchlist_date_windows_departure_date_to", "departure_date_to"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))
    departure_date_from: Mapped[date] = mapped_column(Date, nullable=False)
    departure_date_to: Mapped[date] = mapped_column(Date, nullable=False)
    return_date_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    return_date_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    min_trip_days: Mapped[int | None] = mapped_column(nullable=True)
    max_trip_days: Mapped[int | None] = mapped_column(nullable=True)

    watchlist: Mapped[Watchlist] = relationship(back_populates="date_windows")


class WatchlistSegment(TimestampMixin, Base):
    __tablename__ = "watchlist_segments"
    __table_args__ = (
        CheckConstraint("segment_order >= 1", name="segment_order_positive"),
        CheckConstraint("length(origin_code) = 3", name="segment_origin_code_iata_length"),
        CheckConstraint(
            "length(destination_code) = 3", name="segment_destination_code_iata_length"
        ),
        CheckConstraint("date_from <= date_to", name="segment_date_order"),
        Index("ix_watchlist_segments_watchlist_id", "watchlist_id"),
        Index("ix_watchlist_segments_segment_order", "segment_order"),
        Index("ix_watchlist_segments_origin_code", "origin_code"),
        Index("ix_watchlist_segments_destination_code", "destination_code"),
        Index(
            "uq_watchlist_segments_watchlist_id_segment_order",
            "watchlist_id",
            "segment_order",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))
    segment_order: Mapped[int] = mapped_column(nullable=False)
    origin_code: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_code: Mapped[str] = mapped_column(String(3), nullable=False)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)

    watchlist: Mapped[Watchlist] = relationship(back_populates="segments")
