from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import AlertStatus, AlertType, NotificationChannel


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    watchlist_id: int
    flight_offer_id: int
    alert_type: AlertType
    status: AlertStatus
    message: str
    sent_to: str | None
    sent_channel: NotificationChannel | None
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime
