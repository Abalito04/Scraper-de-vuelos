from datetime import date
from decimal import Decimal

import pytest

from app.core.config import Settings
from app.core.enums import CabinClass, ProviderName, TripType
from app.providers import (
    FlightSearchRequest,
    FlightSearchSegment,
    MockFlightProvider,
    ProviderManager,
)
from app.providers.manager import ProviderNotConfiguredError


def one_way_request() -> FlightSearchRequest:
    return FlightSearchRequest(
        trip_type=TripType.ONE_WAY,
        origin_code="EZE",
        destination_code="DUB",
        departure_date=date(2027, 5, 10),
        currency="USD",
        adults=1,
        cabin_class=CabinClass.ECONOMY,
        max_results=5,
    )


def test_mock_provider_returns_deterministic_offers() -> None:
    provider = MockFlightProvider(seed=42, min_price=500, max_price=700)
    request = one_way_request()

    first = provider.search(request)
    second = provider.search(request)

    assert first == second
    assert 1 <= len(first) <= request.max_results
    assert first[0].provider == ProviderName.MOCK
    assert first[0].origin_code == "EZE"
    assert first[0].destination_code == "DUB"
    assert first[0].total_price >= Decimal("500.00")
    assert first[0].segments
    assert first[0].raw_payload["mock"] is True


def test_mock_provider_supports_round_trip() -> None:
    provider = MockFlightProvider(seed=42)
    request = FlightSearchRequest(
        trip_type=TripType.ROUND_TRIP,
        origin_code="EZE",
        destination_code="MAD",
        departure_date=date(2027, 4, 1),
        return_date=date(2027, 4, 20),
        currency="USD",
        adults=2,
        cabin_class=CabinClass.PREMIUM_ECONOMY,
        max_results=3,
    )

    offers = provider.search(request)

    assert offers
    assert offers[0].trip_type == TripType.ROUND_TRIP
    assert offers[0].return_date == date(2027, 4, 20)
    assert len(offers[0].segments) == 2


def test_mock_provider_supports_multi_city() -> None:
    provider = MockFlightProvider(seed=42)
    request = FlightSearchRequest(
        trip_type=TripType.MULTI_CITY,
        origin_code="EZE",
        destination_code="EZE",
        departure_date=date(2027, 4, 1),
        segments=[
            FlightSearchSegment(
                origin_code="EZE",
                destination_code="MAD",
                departure_date=date(2027, 4, 1),
            ),
            FlightSearchSegment(
                origin_code="MAD",
                destination_code="DUB",
                departure_date=date(2027, 4, 15),
            ),
            FlightSearchSegment(
                origin_code="DUB",
                destination_code="EZE",
                departure_date=date(2027, 5, 1),
            ),
        ],
        currency="USD",
        max_results=4,
    )

    offers = provider.search(request)

    assert offers
    assert offers[0].trip_type == TripType.MULTI_CITY
    assert len(offers[0].segments) == 3
    assert offers[0].segments[1].origin_code == "MAD"


def test_provider_manager_uses_configured_mock_provider() -> None:
    settings = Settings(
        flight_provider="mock",
        mock_provider_seed=7,
        mock_provider_min_price=300,
        mock_provider_max_price=350,
    )
    manager = ProviderManager(settings=settings)

    offers = manager.search(one_way_request())

    assert manager.get_provider_names() == [ProviderName.MOCK]
    assert offers
    assert all(offer.provider == ProviderName.MOCK for offer in offers)


def test_provider_manager_rejects_unsupported_provider() -> None:
    settings = Settings(flight_provider="amadeus")

    with pytest.raises(ProviderNotConfiguredError):
        ProviderManager(settings=settings)


def test_round_trip_request_requires_return_date() -> None:
    with pytest.raises(ValueError):
        FlightSearchRequest(
            trip_type=TripType.ROUND_TRIP,
            origin_code="EZE",
            destination_code="MAD",
            departure_date=date(2027, 4, 1),
        )
