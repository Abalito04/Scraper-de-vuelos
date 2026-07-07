from abc import ABC, abstractmethod

from app.core.enums import ProviderName
from app.providers.normalized import FlightSearchRequest, NormalizedFlightOffer


class FlightSearchProvider(ABC):
    name: ProviderName

    @abstractmethod
    def search(self, request: FlightSearchRequest) -> list[NormalizedFlightOffer]:
        raise NotImplementedError
