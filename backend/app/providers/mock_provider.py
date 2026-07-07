from datetime import timedelta
from decimal import Decimal
from hashlib import sha256
from random import Random

from app.core.enums import ProviderName, TripType
from app.providers.base import FlightSearchProvider
from app.providers.normalized import (
    FlightSearchRequest,
    NormalizedFlightOffer,
    NormalizedFlightSegment,
)


class MockFlightProvider(FlightSearchProvider):
    name = ProviderName.MOCK

    def __init__(
        self,
        *,
        seed: int = 12345,
        min_price: int = 500,
        max_price: int = 1800,
    ) -> None:
        self.seed = seed
        self.min_price = min_price
        self.max_price = max_price

    def search(self, request: FlightSearchRequest) -> list[NormalizedFlightOffer]:
        rng = Random(self._request_seed(request))
        offer_count = rng.randint(1, request.max_results)
        return [self._build_offer(request, index, rng) for index in range(offer_count)]

    def _build_offer(
        self,
        request: FlightSearchRequest,
        index: int,
        rng: Random,
    ) -> NormalizedFlightOffer:
        base_price = rng.randint(self.min_price, self.max_price)
        cabin_multiplier = {
            "ECONOMY": Decimal("1.00"),
            "PREMIUM_ECONOMY": Decimal("1.45"),
            "BUSINESS": Decimal("2.60"),
            "FIRST": Decimal("4.00"),
        }[request.cabin_class.value]
        trip_multiplier = {
            TripType.ONE_WAY: Decimal("1.00"),
            TripType.ROUND_TRIP: Decimal("1.75"),
            TripType.MULTI_CITY: Decimal("2.15"),
        }[request.trip_type]
        total_price = (
            Decimal(base_price) * cabin_multiplier * trip_multiplier * Decimal(request.adults)
        ).quantize(Decimal("0.01"))

        airline_pool = ["AR", "IB", "LA", "AV", "AF", "KL", "UX", "EI"]
        airline_codes = sorted(rng.sample(airline_pool, k=rng.randint(1, 2)))
        stops = rng.randint(0, 2)
        duration_minutes = self._duration_for(request, rng, stops)
        segments = self._segments_for(request, airline_codes[0], stops, duration_minutes)

        return NormalizedFlightOffer(
            provider=self.name,
            provider_offer_id=self._offer_id(request, index),
            origin_code=request.origin_code,
            destination_code=request.destination_code,
            trip_type=request.trip_type,
            departure_date=request.departure_date,
            return_date=request.return_date,
            total_price=total_price,
            currency=request.currency,
            airline_codes=airline_codes,
            stops=stops,
            duration_minutes=duration_minutes,
            deep_link=f"https://example.com/fareradar/mock/{self._offer_id(request, index)}",
            segments=segments,
            raw_payload={
                "mock": True,
                "seed": self.seed,
                "request_hash": self._request_hash(request),
                "rank": index + 1,
            },
        )

    def _segments_for(
        self,
        request: FlightSearchRequest,
        airline_code: str,
        stops: int,
        duration_minutes: int,
    ) -> list[NormalizedFlightSegment]:
        if request.trip_type == TripType.MULTI_CITY:
            per_segment_duration = max(90, duration_minutes // len(request.segments))
            return [
                NormalizedFlightSegment(
                    origin_code=segment.origin_code,
                    destination_code=segment.destination_code,
                    departure_date=segment.departure_date,
                    arrival_date=segment.departure_date + timedelta(days=1),
                    airline_code=airline_code,
                    stops=stops,
                    duration_minutes=per_segment_duration,
                )
                for segment in request.segments
            ]

        outbound = NormalizedFlightSegment(
            origin_code=request.origin_code,
            destination_code=request.destination_code,
            departure_date=request.departure_date,
            arrival_date=request.departure_date + timedelta(days=1),
            airline_code=airline_code,
            stops=stops,
            duration_minutes=duration_minutes if request.trip_type == TripType.ONE_WAY else duration_minutes // 2,
        )
        if request.trip_type == TripType.ONE_WAY:
            return [outbound]

        assert request.return_date is not None
        inbound = NormalizedFlightSegment(
            origin_code=request.destination_code,
            destination_code=request.origin_code,
            departure_date=request.return_date,
            arrival_date=request.return_date + timedelta(days=1),
            airline_code=airline_code,
            stops=stops,
            duration_minutes=duration_minutes - outbound.duration_minutes,
        )
        return [outbound, inbound]

    def _duration_for(self, request: FlightSearchRequest, rng: Random, stops: int) -> int:
        if request.trip_type == TripType.MULTI_CITY:
            return rng.randint(360, 840) * len(request.segments) + stops * 80
        if request.trip_type == TripType.ROUND_TRIP:
            return rng.randint(1100, 2300) + stops * 90
        return rng.randint(650, 1400) + stops * 75

    def _request_seed(self, request: FlightSearchRequest) -> int:
        digest = self._request_hash(request)
        return int(digest[:16], 16)

    def _request_hash(self, request: FlightSearchRequest) -> str:
        payload = request.model_dump_json()
        return sha256(f"{self.seed}:{payload}".encode()).hexdigest()

    def _offer_id(self, request: FlightSearchRequest, index: int) -> str:
        return f"mock-{self._request_hash(request)[:12]}-{index + 1}"
