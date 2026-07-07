from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_session
from app.db.base import Base
from app.main import app


def build_client() -> TestClient:
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
    return TestClient(app)


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def round_trip_payload() -> dict:
    return {
        "name": "Europa 2027",
        "trip_type": "ROUND_TRIP",
        "origins": ["eze", "AEP", "MVD"],
        "destinations": ["DUB", "MAD"],
        "date_windows": [
            {
                "departure_date_from": "2027-03-01",
                "departure_date_to": "2027-06-30",
                "return_date_from": None,
                "return_date_to": None,
                "min_trip_days": 14,
                "max_trip_days": 35,
            }
        ],
        "currency": "usd",
        "max_price": "900.00",
        "max_stops": 2,
        "max_duration_minutes": 2400,
        "cabin_class": "ECONOMY",
        "adults": 1,
        "active": True,
        "check_frequency_hours": 12,
        "alert_rules": {
            "below_max_price": True,
            "below_historical_average_percent": "20.00",
            "new_historical_minimum": True,
            "cooldown_hours": 24,
        },
    }


def test_create_list_get_update_and_delete_watchlist() -> None:
    client = build_client()
    try:
        create_response = client.post("/api/v1/watchlists", json=round_trip_payload())
        assert create_response.status_code == 201
        created = create_response.json()
        assert created["name"] == "Europa 2027"
        assert created["trip_type"] == "ROUND_TRIP"
        assert created["origins"] == ["AEP", "EZE", "MVD"]
        assert created["currency"] == "USD"

        list_response = client.get("/api/v1/watchlists")
        assert list_response.status_code == 200
        listed = list_response.json()
        assert listed["total"] == 1
        assert listed["items"][0]["id"] == created["id"]

        get_response = client.get(f"/api/v1/watchlists/{created['id']}")
        assert get_response.status_code == 200
        assert get_response.json()["destinations"] == ["DUB", "MAD"]

        patch_response = client.patch(
            f"/api/v1/watchlists/{created['id']}",
            json={"name": "Europa primavera 2027", "max_price": "850.00", "active": True},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["name"] == "Europa primavera 2027"
        assert patch_response.json()["max_price"] == "850.00"

        delete_response = client.delete(f"/api/v1/watchlists/{created['id']}")
        assert delete_response.status_code == 204

        inactive_response = client.get("/api/v1/watchlists?active=false")
        assert inactive_response.status_code == 200
        assert inactive_response.json()["total"] == 1
    finally:
        clear_overrides()


def test_create_multi_city_watchlist() -> None:
    client = build_client()
    try:
        response = client.post(
            "/api/v1/watchlists",
            json={
                "name": "Europa multi-city",
                "trip_type": "MULTI_CITY",
                "segments": [
                    {
                        "origin_code": "EZE",
                        "destination_code": "MAD",
                        "date_from": "2027-04-01",
                        "date_to": "2027-04-10",
                    },
                    {
                        "origin_code": "MAD",
                        "destination_code": "DUB",
                        "date_from": "2027-04-15",
                        "date_to": "2027-04-20",
                    },
                ],
                "max_price": "1200.00",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["trip_type"] == "MULTI_CITY"
        assert data["segments"][0]["segment_order"] == 1
        assert data["segments"][1]["destination_code"] == "DUB"
    finally:
        clear_overrides()


def test_rejects_invalid_watchlist_shape() -> None:
    client = build_client()
    try:
        response = client.post(
            "/api/v1/watchlists",
            json={
                "name": "Invalid",
                "trip_type": "ROUND_TRIP",
                "origins": ["EZE"],
                "destinations": ["DUB"],
                "date_windows": [
                    {
                        "departure_date_from": "2027-03-01",
                        "departure_date_to": "2027-06-30",
                    }
                ],
            },
        )

        assert response.status_code == 422
    finally:
        clear_overrides()


def test_returns_404_for_missing_watchlist() -> None:
    client = build_client()
    try:
        response = client.get("/api/v1/watchlists/999")
        assert response.status_code == 404
    finally:
        clear_overrides()
