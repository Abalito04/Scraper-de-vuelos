from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FlightOffer


class FlightOfferRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_duplicate(self, offer: FlightOffer) -> FlightOffer | None:
        return self.db.scalar(
            select(FlightOffer).where(
                FlightOffer.watchlist_id == offer.watchlist_id,
                FlightOffer.provider == offer.provider,
                FlightOffer.origin_code == offer.origin_code,
                FlightOffer.destination_code == offer.destination_code,
                FlightOffer.departure_date == offer.departure_date,
                FlightOffer.return_date == offer.return_date,
                FlightOffer.total_price == offer.total_price,
                FlightOffer.airline_codes == offer.airline_codes,
                FlightOffer.stops == offer.stops,
            )
        )

    def add_if_new(self, offer: FlightOffer) -> tuple[FlightOffer, bool]:
        duplicate = self.find_duplicate(offer)
        if duplicate is not None:
            return duplicate, False
        self.db.add(offer)
        self.db.flush()
        return offer, True
