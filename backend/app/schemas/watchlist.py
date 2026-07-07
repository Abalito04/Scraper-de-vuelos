from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import CabinClass, TripType


def normalize_iata(value: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError("must be a 3-letter IATA code")
    return normalized


class AlertRulesIn(BaseModel):
    below_max_price: bool = True
    below_historical_average_percent: Decimal | None = Field(default=None, gt=0)
    new_historical_minimum: bool = True
    cooldown_hours: int = Field(default=24, ge=0)


class WatchlistDateWindowIn(BaseModel):
    departure_date_from: date
    departure_date_to: date
    return_date_from: date | None = None
    return_date_to: date | None = None
    min_trip_days: int | None = Field(default=None, ge=1)
    max_trip_days: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_dates(self) -> "WatchlistDateWindowIn":
        if self.departure_date_from > self.departure_date_to:
            raise ValueError("departure_date_from cannot be after departure_date_to")
        if self.return_date_from and self.return_date_to and self.return_date_from > self.return_date_to:
            raise ValueError("return_date_from cannot be after return_date_to")
        if self.min_trip_days and self.max_trip_days and self.min_trip_days > self.max_trip_days:
            raise ValueError("min_trip_days cannot be greater than max_trip_days")
        return self


class WatchlistSegmentIn(BaseModel):
    origin_code: str
    destination_code: str
    date_from: date
    date_to: date

    @field_validator("origin_code", "destination_code")
    @classmethod
    def validate_iata(cls, value: str) -> str:
        return normalize_iata(value)

    @model_validator(mode="after")
    def validate_dates(self) -> "WatchlistSegmentIn":
        if self.date_from > self.date_to:
            raise ValueError("date_from cannot be after date_to")
        return self


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    trip_type: TripType
    origins: list[str] = Field(default_factory=list)
    destinations: list[str] = Field(default_factory=list)
    date_windows: list[WatchlistDateWindowIn] = Field(default_factory=list)
    segments: list[WatchlistSegmentIn] = Field(default_factory=list)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    max_price: Decimal | None = Field(default=None, gt=0)
    max_stops: int = Field(default=2, ge=0)
    max_duration_minutes: int | None = Field(default=None, gt=0)
    cabin_class: CabinClass = CabinClass.ECONOMY
    adults: int = Field(default=1, ge=1)
    active: bool = True
    check_frequency_hours: int = Field(default=12, ge=1)
    alert_rules: AlertRulesIn = Field(default_factory=AlertRulesIn)

    @field_validator("origins", "destinations")
    @classmethod
    def validate_iata_list(cls, values: list[str]) -> list[str]:
        return sorted(set(normalize_iata(value) for value in values))

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency must be a 3-letter code")
        return normalized

    @model_validator(mode="after")
    def validate_trip_shape(self) -> "WatchlistCreate":
        if self.trip_type == TripType.MULTI_CITY:
            if len(self.segments) < 2:
                raise ValueError("MULTI_CITY watchlists require at least 2 segments")
            if self.origins or self.destinations or self.date_windows:
                raise ValueError("MULTI_CITY watchlists must use segments instead of origins/destinations/date_windows")
            return self

        if not self.origins:
            raise ValueError("ONE_WAY and ROUND_TRIP watchlists require at least one origin")
        if not self.destinations:
            raise ValueError("ONE_WAY and ROUND_TRIP watchlists require at least one destination")
        if not self.date_windows:
            raise ValueError("ONE_WAY and ROUND_TRIP watchlists require at least one date window")
        if self.segments:
            raise ValueError("segments only apply to MULTI_CITY watchlists")
        if self.trip_type == TripType.ROUND_TRIP:
            for window in self.date_windows:
                if window.min_trip_days is None or window.max_trip_days is None:
                    raise ValueError("ROUND_TRIP date windows require min_trip_days and max_trip_days")
        return self


class WatchlistUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    max_price: Decimal | None = Field(default=None, gt=0)
    max_stops: int | None = Field(default=None, ge=0)
    max_duration_minutes: int | None = Field(default=None, gt=0)
    cabin_class: CabinClass | None = None
    adults: int | None = Field(default=None, ge=1)
    active: bool | None = None
    check_frequency_hours: int | None = Field(default=None, ge=1)
    alert_rules: AlertRulesIn | None = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency must be a 3-letter code")
        return normalized


class WatchlistDateWindowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    departure_date_from: date
    departure_date_to: date
    return_date_from: date | None
    return_date_to: date | None
    min_trip_days: int | None
    max_trip_days: int | None


class WatchlistSegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    segment_order: int
    origin_code: str
    destination_code: str
    date_from: date
    date_to: date


class AlertRulesOut(BaseModel):
    below_max_price: bool
    below_historical_average_percent: Decimal | None
    new_historical_minimum: bool
    cooldown_hours: int


class WatchlistSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    trip_type: TripType
    active: bool
    currency: str
    max_price: Decimal | None
    last_checked_at: datetime | None


class WatchlistRead(WatchlistSummary):
    origins: list[str]
    destinations: list[str]
    date_windows: list[WatchlistDateWindowOut]
    segments: list[WatchlistSegmentOut]
    max_stops: int
    max_duration_minutes: int | None
    cabin_class: CabinClass
    adults: int
    check_frequency_hours: int
    alert_rules: AlertRulesOut
    created_at: datetime
    updated_at: datetime
