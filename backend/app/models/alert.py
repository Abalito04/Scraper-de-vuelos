from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AlertStatus, AlertType, NotificationChannel
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.flight_offer import FlightOffer
    from app.models.watchlist import Watchlist


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_watchlist_id", "watchlist_id"),
        Index("ix_alerts_flight_offer_id", "flight_offer_id"),
        Index("ix_alerts_alert_type", "alert_type"),
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_sent_at", "sent_at"),
        Index("ix_alerts_created_at", "created_at"),
        Index(
            "uq_alerts_watchlist_offer_type_channel",
            "watchlist_id",
            "flight_offer_id",
            "alert_type",
            "sent_channel",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"))
    flight_offer_id: Mapped[int] = mapped_column(ForeignKey("flight_offers.id", ondelete="CASCADE"))
    alert_type: Mapped[AlertType] = mapped_column(
        Enum(AlertType, native_enum=False, length=32),
        nullable=False,
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, native_enum=False, length=32),
        default=AlertStatus.CANDIDATE,
        nullable=False,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_channel: Mapped[NotificationChannel | None] = mapped_column(
        Enum(NotificationChannel, native_enum=False, length=20),
        nullable=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    watchlist: Mapped[Watchlist] = relationship(back_populates="alerts")
    flight_offer: Mapped[FlightOffer] = relationship(back_populates="alerts")
