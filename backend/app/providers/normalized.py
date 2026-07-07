from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.core.enums import CabinClass, ProviderName, TripType


class FlightSearchSegment(BaseModel):
    origin_code: str = Field(min_length=3, max_length=3)
    destination_code: str = Field(min_length=3, max_length=3)
    departure_date: date


class FlightSearchRequest(BaseModel):
    trip_type: TripType
    origin_code: str = Field(min_length=3, max_length=3)
    destination_code: str = Field(min_length=3, max_length=3)
    departure_date: date
    return_date: date | None = None
    segments: list[FlightSearchSegment] = Field(default_factory=list)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    adults: int = Field(default=1, ge=1)
    cabin_class: CabinClass = CabinClass.ECONOMY
    max_results: int = Field(default=10, ge=1, le=50)

    @model_validator(mode="after")
    def validate_trip_shape(self) -> "FlightSearchRequest":
        if self.trip_type == TripType.ROUND_TRIP and self.return_date is None:
            raise ValueError("ROUND_TRIP searches require return_date")
        if self.trip_type == TripType.MULTI_CITY and len(self.segments) < 2:
            raise ValueError("MULTI_CITY searches require at least 2 segments")
        return self


class NormalizedFlightSegment(BaseModel):
    origin_code: str
    destination_code: str
    departure_date: date
    arrival_date: date | None = None
    airline_code: str | None = None
    stops: int = Field(ge=0)
    duration_minutes: int = Field(gt=0)


class NormalizedFlightOffer(BaseModel):
    provider: ProviderName
    provider_offer_id: str
    origin_code: str
    destination_code: str
    trip_type: TripType
    departure_date: date
    return_date: date | None = None
    total_price: Decimal = Field(gt=0)
    currency: str
    airline_codes: list[str] = Field(default_factory=list)
    stops: int = Field(ge=0)
    duration_minutes: int = Field(gt=0)
    deep_link: str | None = None
    segments: list[NormalizedFlightSegment] = Field(default_factory=list)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
