from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import AlertType, NotificationChannel
from app.models import Alert, PriceSnapshot


class AlertRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, alert: Alert) -> Alert:
        self.db.add(alert)
        self.db.flush()
        self.db.refresh(alert)
        return alert

    def recent_duplicate(
        self,
        *,
        watchlist_id: int,
        flight_offer_id: int,
        alert_type: AlertType,
        channel: NotificationChannel,
        cooldown_hours: int,
        now: datetime,
    ) -> Alert | None:
        cutoff = now - timedelta(hours=cooldown_hours)
        return self.db.scalar(
            select(Alert).where(
                Alert.watchlist_id == watchlist_id,
                Alert.flight_offer_id == flight_offer_id,
                Alert.alert_type == alert_type,
                Alert.sent_channel == channel,
                Alert.created_at >= cutoff,
            )
        )

    def average_price(self, watchlist_id: int) -> Decimal | None:
        value = self.db.scalar(
            select(func.avg(PriceSnapshot.price)).where(PriceSnapshot.watchlist_id == watchlist_id)
        )
        return Decimal(str(value)) if value is not None else None

    def minimum_price(self, watchlist_id: int) -> Decimal | None:
        value = self.db.scalar(
            select(func.min(PriceSnapshot.price)).where(PriceSnapshot.watchlist_id == watchlist_id)
        )
        return Decimal(str(value)) if value is not None else None

    def list(
        self,
        *,
        watchlist_id: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Alert], int]:
        filters = []
        if watchlist_id is not None:
            filters.append(Alert.watchlist_id == watchlist_id)
        total = self.db.scalar(select(func.count()).select_from(Alert).where(*filters)) or 0
        items = list(
            self.db.scalars(
                self._base_query()
                .where(*filters)
                .order_by(Alert.created_at.desc(), Alert.id.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        return items, total

    def _base_query(self) -> Select[tuple[Alert]]:
        return select(Alert).options(selectinload(Alert.flight_offer))
