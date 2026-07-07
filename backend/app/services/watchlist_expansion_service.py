from datetime import date, timedelta

from app.core.enums import TripType
from app.models import Watchlist
from app.providers.normalized import FlightSearchRequest, FlightSearchSegment


class TooManyCombinationsError(Exception):
    pass


class WatchlistExpansionService:
    def __init__(self, *, max_combinations: int = 200, max_results_per_request: int = 10) -> None:
        self.max_combinations = max_combinations
        self.max_results_per_request = max_results_per_request

    def expand(self, watchlist: Watchlist) -> list[FlightSearchRequest]:
        if watchlist.trip_type == TripType.MULTI_CITY:
            return [self._multi_city_request(watchlist)]

        requests: list[FlightSearchRequest] = []
        for origin in watchlist.origins:
            for destination in watchlist.destinations:
                for window in watchlist.date_windows:
                    departure = window.departure_date_from
                    while departure <= window.departure_date_to:
                        if watchlist.trip_type == TripType.ONE_WAY:
                            requests.append(
                                self._request(
                                    watchlist=watchlist,
                                    origin_code=origin.origin_code,
                                    destination_code=destination.destination_code,
                                    departure_date=departure,
                                )
                            )
                        else:
                            min_days = window.min_trip_days or 1
                            max_days = window.max_trip_days or min_days
                            for trip_days in range(min_days, max_days + 1):
                                return_date = departure + timedelta(days=trip_days)
                                if window.return_date_from and return_date < window.return_date_from:
                                    continue
                                if window.return_date_to and return_date > window.return_date_to:
                                    continue
                                requests.append(
                                    self._request(
                                        watchlist=watchlist,
                                        origin_code=origin.origin_code,
                                        destination_code=destination.destination_code,
                                        departure_date=departure,
                                        return_date=return_date,
                                    )
                                )
                        self._ensure_limit(requests)
                        departure += timedelta(days=1)
        return requests

    def _request(
        self,
        *,
        watchlist: Watchlist,
        origin_code: str,
        destination_code: str,
        departure_date: date,
        return_date: date | None = None,
    ) -> FlightSearchRequest:
        return FlightSearchRequest(
            trip_type=watchlist.trip_type,
            origin_code=origin_code,
            destination_code=destination_code,
            departure_date=departure_date,
            return_date=return_date,
            currency=watchlist.currency,
            adults=watchlist.adults,
            cabin_class=watchlist.cabin_class,
            max_results=self.max_results_per_request,
        )

    def _multi_city_request(self, watchlist: Watchlist) -> FlightSearchRequest:
        first_segment = watchlist.segments[0]
        last_segment = watchlist.segments[-1]
        return FlightSearchRequest(
            trip_type=TripType.MULTI_CITY,
            origin_code=first_segment.origin_code,
            destination_code=last_segment.destination_code,
            departure_date=first_segment.date_from,
            segments=[
                FlightSearchSegment(
                    origin_code=segment.origin_code,
                    destination_code=segment.destination_code,
                    departure_date=segment.date_from,
                )
                for segment in watchlist.segments
            ],
            currency=watchlist.currency,
            adults=watchlist.adults,
            cabin_class=watchlist.cabin_class,
            max_results=self.max_results_per_request,
        )

    def _ensure_limit(self, requests: list[FlightSearchRequest]) -> None:
        if len(requests) > self.max_combinations:
            raise TooManyCombinationsError(
                f"Watchlist generated more than {self.max_combinations} search combinations"
            )
