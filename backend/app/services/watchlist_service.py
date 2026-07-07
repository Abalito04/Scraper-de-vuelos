from app.core.enums import TripType
from app.models import (
    Watchlist,
    WatchlistDateWindow,
    WatchlistDestination,
    WatchlistOrigin,
    WatchlistSegment,
)
from app.repositories.watchlist_repository import WatchlistRepository
from app.schemas.common import PaginatedResponse
from app.schemas.watchlist import (
    AlertRulesOut,
    WatchlistCreate,
    WatchlistDateWindowOut,
    WatchlistRead,
    WatchlistSegmentOut,
    WatchlistSummary,
    WatchlistUpdate,
)


class WatchlistNotFoundError(Exception):
    pass


class WatchlistService:
    def __init__(self, repository: WatchlistRepository) -> None:
        self.repository = repository

    def create(self, payload: WatchlistCreate) -> WatchlistRead:
        user = self.repository.get_or_create_dev_user()
        watchlist = Watchlist(
            user=user,
            name=payload.name,
            trip_type=payload.trip_type,
            currency=payload.currency,
            max_price=payload.max_price,
            max_stops=payload.max_stops,
            max_duration_minutes=payload.max_duration_minutes,
            cabin_class=payload.cabin_class,
            adults=payload.adults,
            active=payload.active,
            check_frequency_hours=payload.check_frequency_hours,
            alert_below_max_price=payload.alert_rules.below_max_price,
            alert_below_average_percent=payload.alert_rules.below_historical_average_percent,
            alert_on_new_minimum=payload.alert_rules.new_historical_minimum,
            alert_cooldown_hours=payload.alert_rules.cooldown_hours,
        )
        watchlist.origins = [WatchlistOrigin(origin_code=origin) for origin in payload.origins]
        watchlist.destinations = [
            WatchlistDestination(destination_code=destination)
            for destination in payload.destinations
        ]
        watchlist.date_windows = [
            WatchlistDateWindow(**window.model_dump())
            for window in payload.date_windows
        ]
        watchlist.segments = [
            WatchlistSegment(segment_order=index, **segment.model_dump())
            for index, segment in enumerate(payload.segments, start=1)
        ]

        try:
            self.repository.add(watchlist)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise
        return self.to_read(watchlist)

    def get(self, watchlist_id: int) -> WatchlistRead:
        watchlist = self.repository.get(watchlist_id)
        if watchlist is None:
            raise WatchlistNotFoundError
        return self.to_read(watchlist)

    def list(
        self,
        *,
        active: bool | None,
        trip_type: TripType | None,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[WatchlistSummary]:
        items, total = self.repository.list(
            active=active,
            trip_type=trip_type,
            limit=limit,
            offset=offset,
        )
        return PaginatedResponse[WatchlistSummary](
            items=[self.to_summary(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    def update(self, watchlist_id: int, payload: WatchlistUpdate) -> WatchlistRead:
        watchlist = self.repository.get(watchlist_id)
        if watchlist is None:
            raise WatchlistNotFoundError

        updates = payload.model_dump(exclude_unset=True)
        alert_rules = updates.pop("alert_rules", None)
        for field, value in updates.items():
            setattr(watchlist, field, value)
        if alert_rules is not None:
            watchlist.alert_below_max_price = alert_rules["below_max_price"]
            watchlist.alert_below_average_percent = alert_rules[
                "below_historical_average_percent"
            ]
            watchlist.alert_on_new_minimum = alert_rules["new_historical_minimum"]
            watchlist.alert_cooldown_hours = alert_rules["cooldown_hours"]

        try:
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise
        return self.to_read(watchlist)

    def delete(self, watchlist_id: int) -> None:
        watchlist = self.repository.get(watchlist_id)
        if watchlist is None:
            raise WatchlistNotFoundError
        try:
            self.repository.delete_soft(watchlist)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

    @staticmethod
    def to_summary(watchlist: Watchlist) -> WatchlistSummary:
        return WatchlistSummary.model_validate(watchlist)

    @classmethod
    def to_read(cls, watchlist: Watchlist) -> WatchlistRead:
        summary = cls.to_summary(watchlist).model_dump()
        return WatchlistRead(
            **summary,
            origins=[origin.origin_code for origin in watchlist.origins],
            destinations=[
                destination.destination_code for destination in watchlist.destinations
            ],
            date_windows=[
                WatchlistDateWindowOut.model_validate(window)
                for window in watchlist.date_windows
            ],
            segments=[
                WatchlistSegmentOut.model_validate(segment)
                for segment in watchlist.segments
            ],
            max_stops=watchlist.max_stops,
            max_duration_minutes=watchlist.max_duration_minutes,
            cabin_class=watchlist.cabin_class,
            adults=watchlist.adults,
            check_frequency_hours=watchlist.check_frequency_hours,
            alert_rules=AlertRulesOut(
                below_max_price=watchlist.alert_below_max_price,
                below_historical_average_percent=watchlist.alert_below_average_percent,
                new_historical_minimum=watchlist.alert_on_new_minimum,
                cooldown_hours=watchlist.alert_cooldown_hours,
            ),
            created_at=watchlist.created_at,
            updated_at=watchlist.updated_at,
        )
