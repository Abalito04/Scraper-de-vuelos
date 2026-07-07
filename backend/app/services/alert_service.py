from datetime import UTC, datetime

from app.core.config import Settings, get_settings
from app.core.enums import AlertStatus, NotificationChannel
from app.models import Alert, FlightOffer, Watchlist
from app.notifications import NotificationMessage, NotificationService
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertRead
from app.schemas.common import PaginatedResponse
from app.services.alert_rules_engine import AlertCandidate, AlertRulesEngine


class AlertService:
    def __init__(
        self,
        *,
        alert_repository: AlertRepository,
        notification_service: NotificationService | None = None,
        rules_engine: AlertRulesEngine | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.alert_repository = alert_repository
        self.notification_service = notification_service or NotificationService()
        self.rules_engine = rules_engine or AlertRulesEngine()
        self.settings = settings or get_settings()

    def evaluate_offer(self, *, watchlist: Watchlist, offer: FlightOffer) -> list[Alert]:
        historical_average = self.alert_repository.average_price(watchlist.id)
        historical_minimum = self.alert_repository.minimum_price(watchlist.id)
        candidates = self.rules_engine.evaluate(
            watchlist=watchlist,
            offer=offer,
            historical_average=historical_average,
            historical_minimum=historical_minimum,
        )
        return [self._create_or_skip(watchlist=watchlist, offer=offer, candidate=candidate) for candidate in candidates]

    def list(
        self,
        *,
        watchlist_id: int | None,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[AlertRead]:
        items, total = self.alert_repository.list(
            watchlist_id=watchlist_id,
            limit=limit,
            offset=offset,
        )
        return PaginatedResponse[AlertRead](
            items=[AlertRead.model_validate(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    def _create_or_skip(
        self,
        *,
        watchlist: Watchlist,
        offer: FlightOffer,
        candidate: AlertCandidate,
    ) -> Alert:
        now = datetime.now(UTC)
        channel = NotificationChannel.TELEGRAM
        recipient = watchlist.user.telegram_chat_id or self.settings.telegram_default_chat_id
        message = self._format_message(watchlist=watchlist, offer=offer, reason=candidate.reason)

        duplicate = self.alert_repository.recent_duplicate(
            watchlist_id=watchlist.id,
            flight_offer_id=offer.id,
            alert_type=candidate.alert_type,
            channel=channel,
            cooldown_hours=watchlist.alert_cooldown_hours,
            now=now,
        )
        if duplicate is not None:
            return duplicate

        alert = Alert(
            watchlist_id=watchlist.id,
            flight_offer_id=offer.id,
            alert_type=candidate.alert_type,
            status=AlertStatus.PENDING,
            message=message,
            sent_channel=channel,
            sent_to=recipient,
        )

        if recipient:
            result = self.notification_service.send(
                NotificationMessage(recipient=recipient, text=message)
            )
            if result.success:
                alert.status = AlertStatus.SENT
                alert.sent_at = now
            else:
                alert.status = AlertStatus.FAILED
                alert.error_message = result.error_message
        else:
            alert.status = AlertStatus.PENDING

        return self.alert_repository.add(alert)

    def _format_message(self, *, watchlist: Watchlist, offer: FlightOffer, reason: str) -> str:
        dates = str(offer.departure_date)
        if offer.return_date:
            dates = f"{offer.departure_date} a {offer.return_date}"
        return (
            f"FareRadar: {watchlist.name}\n"
            f"Ruta: {offer.origin_code} -> {offer.destination_code}\n"
            f"Fechas: {dates}\n"
            f"Precio: {offer.currency} {offer.total_price}\n"
            f"Escalas: {offer.stops}\n"
            f"Duracion: {offer.duration_minutes or 'N/D'} min\n"
            f"Motivo: {reason}\n"
            f"Link: {offer.deep_link or 'N/D'}"
        )
