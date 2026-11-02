from fastapi.testclient import TestClient

from api import main

client = TestClient(main.app)


def test_health_endpoint_reports_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "X-Request-ID" in response.headers


def test_predict_rejects_unknown_ticker() -> None:
    response = client.post("/predict", json={"ticker": "NOPE", "features": {"x": 1}})

    assert response.status_code == 422


def test_predict_returns_model_metadata(monkeypatch) -> None:
    monkeypatch.setattr(main, "load_model_artifact", lambda ticker, model_dir: {
        "ticker": ticker,
        "model_name": "LinearRegression",
        "model_version": "test-version",
    })
    monkeypatch.setattr(main, "predict_from_features", lambda artifact, features: 123.45)

    response = client.post("/predict", json={"ticker": "aapl", "features": {"feature": 1.0}})

    assert response.status_code == 200
    assert response.json()["prediction"] == 123.45
    assert response.json()["model_version"] == "test-version"


def test_predict_reports_missing_artifact(monkeypatch) -> None:
    def missing_artifact(ticker, model_dir):
        raise FileNotFoundError("No trained model for AAPL")

    monkeypatch.setattr(main, "load_model_artifact", missing_artifact)

    response = client.post("/predict", json={"ticker": "AAPL", "features": {"feature": 1.0}})

    assert response.status_code == 404