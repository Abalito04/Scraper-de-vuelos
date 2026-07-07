from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_status() -> None:
    response = client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json()["app"] == "FareRadar"
    assert response.json()["version"] == "0.1.0"
    assert response.json()["provider"] == "mock"
