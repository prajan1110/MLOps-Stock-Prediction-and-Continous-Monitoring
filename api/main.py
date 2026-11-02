"""FastAPI inference service for trained stock model artifacts."""

import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from monitoring.logging_config import configure_logging
from src.config import ALL_STOCKS
from src.predict import load_model_artifact, predict_from_features

configure_logging()
logger = logging.getLogger("stock_api")
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models"))
app = FastAPI(title="Stock Prediction API", version="1.0.0")


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1, max_length=20)
    features: dict[str, float]

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


@app.middleware("http")
async def log_request_metrics(request: Request, call_next):
    request_id = uuid.uuid4().hex
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed request_id=%s path=%s", request_id, request.url.path)
        raise

    latency_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s latency_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
    )
    return response


@app.get("/health")
def health() -> dict[str, object]:
    model_count = sum(1 for _ in MODEL_DIR.glob("*.joblib")) if MODEL_DIR.exists() else 0
    return {"status": "ok", "models_available": model_count}


@app.get("/model-info")
def model_info(ticker: str | None = None) -> dict[str, object]:
    requested = ticker.strip().upper() if ticker else None
    if requested and requested not in ALL_STOCKS:
        raise HTTPException(status_code=422, detail="Unsupported ticker")

    artifacts = []
    for path in sorted(MODEL_DIR.glob("*.joblib")) if MODEL_DIR.exists() else []:
        try:
            artifact = joblib.load(path)
        except Exception:
            logger.exception("Could not load model metadata from %s", path)
            continue
        if requested and artifact.get("ticker") != requested:
            continue
        artifacts.append(
            {
                "ticker": artifact.get("ticker"),
                "model_name": artifact.get("model_name"),
                "model_version": artifact.get("model_version"),
                "trained_at": artifact.get("trained_at"),
                "dataset_sha256": artifact.get("dataset_sha256"),
                "feature_columns": artifact.get("feature_columns"),
                "validation_metrics": artifact.get("validation_metrics"),
                "test_metrics": artifact.get("test_metrics"),
            }
        )
    return {"models": artifacts}


@app.post("/predict")
def predict(request: PredictionRequest) -> dict[str, object]:
    if request.ticker not in ALL_STOCKS:
        raise HTTPException(status_code=422, detail="Unsupported ticker")
    try:
        artifact = load_model_artifact(request.ticker, MODEL_DIR)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    try:
        value = predict_from_features(artifact, request.features)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return {
        "ticker": request.ticker,
        "prediction": value,
        "model_name": artifact["model_name"],
        "model_version": artifact["model_version"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }