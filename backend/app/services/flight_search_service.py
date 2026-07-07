from hashlib import sha256
from time import perf_counter

from app.core.config import Settings, get_settings
from app.core.enums import ProviderLogStatus
from app.models import FlightOffer, PriceSnapshot, ProviderLog
from app.providers import ProviderManager
from app.providers.normalized import FlightSearchRequest, NormalizedFlightOffer
from app.repositories.flight_offer_repository import FlightOfferRepository
from app.repositories.price_snapshot_repository import PriceSnapshotRepository
from app.repositories.provider_log_repository import ProviderLogRepository
from app.repositories.watchlist_repository import WatchlistRepository
from app.schemas.search import ManualSearchResult
from app.services.watchlist_expansion_service import WatchlistExpansionService
from app.services.watchlist_service import WatchlistNotFoundError


class WatchlistInactiveError(Exception):
    pass


class FlightSearchService:
    def __init__(
        self,
        *,
        watchlist_repository: WatchlistRepository,
        flight_offer_repository: FlightOfferRepository,
        price_snapshot_repository: PriceSnapshotRepository,
        provider_log_repository: ProviderLogRepository,
        provider_manager: ProviderManager | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.watchlist_repository = watchlist_repository
        self.flight_offer_repository = flight_offer_repository
        self.price_snapshot_repository = price_snapshot_repository
        self.provider_log_repository = provider_log_repository
        self.settings = settings or get_settings()
        self.provider_manager = provider_manager or ProviderManager(settings=self.settings)
        self.expansion_service = WatchlistExpansionService(
            max_combinations=self.settings.max_combinations_per_watchlist
        )

    def run_manual_search(self, watchlist_id: int) -> ManualSearchResult:
        watchlist = self.watchlist_repository.get(watchlist_id)
        if watchlist is None:
            raise WatchlistNotFoundError
        if not watchlist.active:
            raise WatchlistInactiveError

        requests = self.expansion_service.expand(watchlist)
        offers_found = 0
        offers_created = 0
        snapshots_created = 0
        provider_logs_created = 0

        try:
            for request in requests:
                started_at = perf_counter()
                try:
                    offers = self.provider_manager.search(request)
                    duration_ms = int((perf_counter() - started_at) * 1000)
                    self._add_provider_log(
                        watchlist_id=watchlist.id,
                        request=request,
                        status=ProviderLogStatus.SUCCESS,
                        duration_ms=duration_ms,
                    )
                    provider_logs_created += 1
                except Exception as exc:
                    duration_ms = int((perf_counter() - started_at) * 1000)
                    self._add_provider_log(
                        watchlist_id=watchlist.id,
                        request=request,
                        status=ProviderLogStatus.ERROR,
                        duration_ms=duration_ms,
                        error_message=str(exc),
                    )
                    provider_logs_created += 1
                    raise

                offers_found += len(offers)
                for normalized_offer in offers:
                    offer, created = self._persist_offer(watchlist.id, normalized_offer)
                    if created:
                        offers_created += 1
                    self.price_snapshot_repository.add(
                        PriceSnapshot(
                            watchlist_id=watchlist.id,
                            flight_offer_id=offer.id,
                            price=normalized_offer.total_price,
                            currency=normalized_offer.currency,
                        )
                    )
                    snapshots_created += 1

            self.watchlist_repository.commit()
        except Exception:
            self.watchlist_repository.rollback()
            raise

        provider_names = ",".join(name.value for name in self.provider_manager.get_provider_names())
        return ManualSearchResult(
            watchlist_id=watchlist.id,
            provider=provider_names,
            requests_created=len(requests),
            offers_found=offers_found,
            offers_created=offers_created,
            snapshots_created=snapshots_created,
            provider_logs_created=provider_logs_created,
        )

    def _persist_offer(
        self,
        watchlist_id: int,
        normalized_offer: NormalizedFlightOffer,
    ) -> tuple[FlightOffer, bool]:
        offer = FlightOffer(
            watchlist_id=watchlist_id,
            provider=normalized_offer.provider,
            provider_offer_id=normalized_offer.provider_offer_id,
            origin_code=normalized_offer.origin_code,
            destination_code=normalized_offer.destination_code,
            trip_type=normalized_offer.trip_type,
            departure_date=normalized_offer.departure_date,
            return_date=normalized_offer.return_date,
            total_price=normalized_offer.total_price,
            currency=normalized_offer.currency,
            airline_codes=",".join(normalized_offer.airline_codes),
            stops=normalized_offer.stops,
            duration_minutes=normalized_offer.duration_minutes,
            deep_link=normalized_offer.deep_link,
            raw_payload=normalized_offer.raw_payload,
        )
        return self.flight_offer_repository.add_if_new(offer)

    def _add_provider_log(
        self,
        *,
        watchlist_id: int,
        request: FlightSearchRequest,
        status: ProviderLogStatus,
        duration_ms: int,
        error_message: str | None = None,
    ) -> None:
        self.provider_log_repository.add(
            ProviderLog(
                provider=self.provider_manager.get_provider_names()[0],
                watchlist_id=watchlist_id,
                request_hash=sha256(request.model_dump_json().encode()).hexdigest(),
                status=status,
                duration_ms=duration_ms,
                error_message=error_message,
            )
        )
