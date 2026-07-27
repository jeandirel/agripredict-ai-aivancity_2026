from fastapi.testclient import TestClient

from app.api.main import app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert isinstance(payload["available_models"], list)


def test_unknown_model_returns_503_when_artifact_missing() -> None:
    client = TestClient(app)
    response = client.post(
        "/predict/harvest-date",
        json={"horizon": "may31", "year": 2024, "features": {"SURF_PARC": 5.0}},
    )
    if not client.get("/health").json()["available_models"]:
        assert response.status_code == 503
