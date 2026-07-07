from app.core.config import Settings, get_settings
from app.core.enums import ProviderName
from app.providers.base import FlightSearchProvider
from app.providers.mock_provider import MockFlightProvider
from app.providers.normalized import FlightSearchRequest, NormalizedFlightOffer


class ProviderNotConfiguredError(Exception):
    pass


class ProviderManager:
    def __init__(
        self,
        providers: list[FlightSearchProvider] | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.providers = providers or [self._build_default_provider()]

    def search(self, request: FlightSearchRequest) -> list[NormalizedFlightOffer]:
        offers: list[NormalizedFlightOffer] = []
        for provider in self.providers:
            offers.extend(provider.search(request))
        return offers

    def get_provider_names(self) -> list[ProviderName]:
        return [provider.name for provider in self.providers]

    def _build_default_provider(self) -> FlightSearchProvider:
        provider_name = self.settings.flight_provider.lower()
        if provider_name != "mock":
            raise ProviderNotConfiguredError(f"Unsupported flight provider: {provider_name}")
        return MockFlightProvider(
            seed=self.settings.mock_provider_seed,
            min_price=self.settings.mock_provider_min_price,
            max_price=self.settings.mock_provider_max_price,
        )
