from datetime import date
from decimal import Decimal

from app.core.enums import AlertType, CabinClass, ProviderName, TripType
from app.models import FlightOffer, Watchlist
from app.services.alert_rules_engine import AlertRulesEngine


def test_alert_rules_engine_detects_below_max_price() -> None:
    watchlist = Watchlist(
        id=1,
        name="Europa",
        trip_type=TripType.ROUND_TRIP,
        max_price=Decimal("900.00"),
        max_stops=2,
        max_duration_minutes=2400,
        alert_below_max_price=True,
        alert_on_new_minimum=True,
        cabin_class=CabinClass.ECONOMY,
        adults=1,
        currency="USD",
    )
    offer = FlightOffer(
        id=1,
        watchlist_id=1,
        provider=ProviderName.MOCK,
        origin_code="EZE",
        destination_code="DUB",
        trip_type=TripType.ROUND_TRIP,
        departure_date=date(2027, 5, 10),
        return_date=date(2027, 5, 30),
        total_price=Decimal("820.00"),
        currency="USD",
        stops=1,
        duration_minutes=1200,
    )

    candidates = AlertRulesEngine().evaluate(
        watchlist=watchlist,
        offer=offer,
        historical_average=None,
        historical_minimum=None,
    )

    assert [candidate.alert_type for candidate in candidates] == [AlertType.BELOW_MAX_PRICE]


def test_alert_rules_engine_blocks_too_many_stops() -> None:
    watchlist = Watchlist(
        id=1,
        name="Europa",
        trip_type=TripType.ROUND_TRIP,
        max_price=Decimal("900.00"),
        max_stops=1,
        alert_below_max_price=True,
        cabin_class=CabinClass.ECONOMY,
        adults=1,
        currency="USD",
    )
    offer = FlightOffer(
        id=1,
        watchlist_id=1,
        provider=ProviderName.MOCK,
        origin_code="EZE",
        destination_code="DUB",
        trip_type=TripType.ROUND_TRIP,
        departure_date=date(2027, 5, 10),
        return_date=date(2027, 5, 30),
        total_price=Decimal("700.00"),
        currency="USD",
        stops=2,
        duration_minutes=1200,
    )

    candidates = AlertRulesEngine().evaluate(
        watchlist=watchlist,
        offer=offer,
        historical_average=None,
        historical_minimum=None,
    )

    assert candidates == []
