from dataclasses import dataclass
from decimal import Decimal

from app.core.enums import AlertType
from app.models import FlightOffer, Watchlist


@dataclass(frozen=True)
class AlertCandidate:
    alert_type: AlertType
    reason: str


class AlertRulesEngine:
    def evaluate(
        self,
        *,
        watchlist: Watchlist,
        offer: FlightOffer,
        historical_average: Decimal | None,
        historical_minimum: Decimal | None,
    ) -> list[AlertCandidate]:
        if offer.stops > watchlist.max_stops:
            return []
        if (
            watchlist.max_duration_minutes is not None
            and offer.duration_minutes is not None
            and offer.duration_minutes > watchlist.max_duration_minutes
        ):
            return []

        candidates: list[AlertCandidate] = []
        if (
            watchlist.alert_below_max_price
            and watchlist.max_price is not None
            and offer.total_price <= watchlist.max_price
        ):
            candidates.append(
                AlertCandidate(
                    alert_type=AlertType.BELOW_MAX_PRICE,
                    reason=f"Precio {offer.currency} {offer.total_price} debajo del maximo configurado.",
                )
            )

        if (
            watchlist.alert_below_average_percent is not None
            and historical_average is not None
            and historical_average > 0
        ):
            threshold = historical_average * (
                Decimal("1") - (watchlist.alert_below_average_percent / Decimal("100"))
            )
            if offer.total_price <= threshold:
                candidates.append(
                    AlertCandidate(
                        alert_type=AlertType.BELOW_HISTORICAL_AVERAGE,
                        reason=(
                            f"Precio al menos {watchlist.alert_below_average_percent}% "
                            "por debajo del promedio historico."
                        ),
                    )
                )

        if (
            watchlist.alert_on_new_minimum
            and historical_minimum is not None
            and offer.total_price <= historical_minimum
        ):
            candidates.append(
                AlertCandidate(
                    alert_type=AlertType.NEW_HISTORICAL_MINIMUM,
                    reason="Nuevo minimo historico para esta watchlist.",
                )
            )

        return candidates
