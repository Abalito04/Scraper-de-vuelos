from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.enums import (
    AlertStatus,
    AlertType,
    CabinClass,
    NotificationChannel,
    ProviderLogStatus,
    ProviderName,
    TripType,
)
from app.db.base import Base
from app.models import (
    Alert,
    FlightOffer,
    PriceSnapshot,
    ProviderLog,
    User,
    Watchlist,
    WatchlistDateWindow,
    WatchlistDestination,
    WatchlistOrigin,
    WatchlistSegment,
)


def build_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_can_create_round_trip_watchlist_with_related_rows() -> None:
    session = build_session()
    user = User(name="Demo User", email="demo@example.com")
    watchlist = Watchlist(
        user=user,
        name="Europa 2027",
        trip_type=TripType.ROUND_TRIP,
        currency="USD",
        max_price=Decimal("900.00"),
        max_stops=2,
        cabin_class=CabinClass.ECONOMY,
        adults=1,
        origins=[WatchlistOrigin(origin_code="EZE"), WatchlistOrigin(origin_code="MVD")],
        destinations=[WatchlistDestination(destination_code="DUB")],
        date_windows=[
            WatchlistDateWindow(
                departure_date_from=date(2027, 3, 1),
                departure_date_to=date(2027, 6, 30),
                min_trip_days=14,
                max_trip_days=35,
            )
        ],
    )

    session.add(watchlist)
    session.commit()

    stored = session.scalar(select(Watchlist).where(Watchlist.name == "Europa 2027"))
    assert stored is not None
    assert stored.user.email == "demo@example.com"
    assert len(stored.origins) == 2
    assert stored.destinations[0].destination_code == "DUB"
    assert stored.date_windows[0].min_trip_days == 14
    assert stored.active is True
    assert stored.check_frequency_hours == 12


def test_can_create_multi_city_watchlist_segments() -> None:
    session = build_session()
    user = User(name="Demo User", email="multi@example.com")
    watchlist = Watchlist(
        user=user,
        name="Europa multi-city",
        trip_type=TripType.MULTI_CITY,
        segments=[
            WatchlistSegment(
                segment_order=1,
                origin_code="EZE",
                destination_code="MAD",
                date_from=date(2027, 4, 1),
                date_to=date(2027, 4, 10),
            ),
            WatchlistSegment(
                segment_order=2,
                origin_code="MAD",
                destination_code="DUB",
                date_from=date(2027, 4, 15),
                date_to=date(2027, 4, 20),
            ),
        ],
    )

    session.add(watchlist)
    session.commit()

    stored = session.scalar(select(Watchlist).where(Watchlist.trip_type == TripType.MULTI_CITY))
    assert stored is not None
    assert [segment.segment_order for segment in stored.segments] == [1, 2]


def test_can_create_offer_snapshot_alert_and_provider_log() -> None:
    session = build_session()
    user = User(name="Demo User", email="offers@example.com")
    watchlist = Watchlist(user=user, name="Europa 2027", trip_type=TripType.ROUND_TRIP)
    offer = FlightOffer(
        watchlist=watchlist,
        provider=ProviderName.MOCK,
        provider_offer_id="mock-1",
        origin_code="EZE",
        destination_code="DUB",
        trip_type=TripType.ROUND_TRIP,
        departure_date=date(2027, 5, 10),
        return_date=date(2027, 5, 30),
        total_price=Decimal("820.00"),
        currency="USD",
        airline_codes="IB,EI",
        stops=1,
        duration_minutes=1060,
        raw_payload={"source": "mock"},
    )
    snapshot = PriceSnapshot(
        watchlist=watchlist,
        flight_offer=offer,
        price=Decimal("820.00"),
        currency="USD",
    )
    alert = Alert(
        watchlist=watchlist,
        flight_offer=offer,
        alert_type=AlertType.BELOW_MAX_PRICE,
        status=AlertStatus.SENT,
        message="Oferta detectada",
        sent_channel=NotificationChannel.TELEGRAM,
        sent_to="123456",
    )
    provider_log = ProviderLog(
        provider=ProviderName.MOCK,
        watchlist=watchlist,
        request_hash="abc123",
        status=ProviderLogStatus.SUCCESS,
        duration_ms=120,
    )

    session.add_all([snapshot, alert, provider_log])
    session.commit()

    stored_offer = session.scalar(
        select(FlightOffer).where(FlightOffer.provider_offer_id == "mock-1")
    )
    assert stored_offer is not None
    assert stored_offer.price_snapshots[0].price == Decimal("820.00")
    assert stored_offer.alerts[0].status == AlertStatus.SENT
    assert watchlist.provider_logs[0].status == ProviderLogStatus.SUCCESS
