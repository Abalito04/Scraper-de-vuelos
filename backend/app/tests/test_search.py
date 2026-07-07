from collections.abc import Generator
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_session
from app.core.enums import CabinClass, TripType
from app.db.base import Base
from app.main import app
from app.models import Alert, FlightOffer, PriceSnapshot, ProviderLog, Watchlist, WatchlistSegment
from app.services.watchlist_expansion_service import WatchlistExpansionService


def build_client_and_session() -> tuple[TestClient, sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    def override_get_session() -> Generator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app), TestingSessionLocal


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def small_round_trip_payload() -> dict:
    return {
        "name": "Small search",
        "trip_type": "ROUND_TRIP",
        "origins": ["EZE"],
        "destinations": ["DUB"],
        "date_windows": [
            {
                "departure_date_from": "2027-05-10",
                "departure_date_to": "2027-05-10",
                "min_trip_days": 14,
                "max_trip_days": 14,
            }
        ],
        "max_price": "99999.00",
    }


def test_watchlist_expansion_for_multi_city_creates_single_request() -> None:
    watchlist = Watchlist(
        id=1,
        name="Multi",
        trip_type=TripType.MULTI_CITY,
        currency="USD",
        adults=1,
        cabin_class=CabinClass.ECONOMY,
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

    requests = WatchlistExpansionService().expand(watchlist)

    assert len(requests) == 1
    assert requests[0].trip_type == TripType.MULTI_CITY
    assert len(requests[0].segments) == 2


def test_manual_run_persists_offers_snapshots_and_provider_logs() -> None:
    client, SessionLocal = build_client_and_session()
    try:
        create_response = client.post("/api/v1/watchlists", json=small_round_trip_payload())
        assert create_response.status_code == 201
        watchlist_id = create_response.json()["id"]

        run_response = client.post(f"/api/v1/watchlists/{watchlist_id}/run")
        assert run_response.status_code == 200
        result = run_response.json()
        assert result["watchlist_id"] == watchlist_id
        assert result["provider"] == "MOCK"
        assert result["requests_created"] == 1
        assert result["offers_found"] >= 1
        assert result["offers_created"] >= 1
        assert result["snapshots_created"] == result["offers_found"]
        assert result["provider_logs_created"] == 1
        assert result["alerts_created"] >= result["offers_found"]

        with SessionLocal() as db:
            assert db.scalar(select(func.count()).select_from(FlightOffer)) == result["offers_created"]
            assert (
                db.scalar(select(func.count()).select_from(PriceSnapshot))
                == result["snapshots_created"]
            )
            assert db.scalar(select(func.count()).select_from(ProviderLog)) == 1
            assert db.scalar(select(func.count()).select_from(Alert)) == result["alerts_created"]
    finally:
        clear_overrides()


def test_manual_run_rejects_inactive_watchlist() -> None:
    client, _ = build_client_and_session()
    try:
        create_response = client.post("/api/v1/watchlists", json=small_round_trip_payload())
        watchlist_id = create_response.json()["id"]
        delete_response = client.delete(f"/api/v1/watchlists/{watchlist_id}")
        assert delete_response.status_code == 204

        run_response = client.post(f"/api/v1/watchlists/{watchlist_id}/run")
        assert run_response.status_code == 400
    finally:
        clear_overrides()
