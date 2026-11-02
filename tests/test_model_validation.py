import json

import joblib
import pytest

from monitoring.model_validation import validate_model_bundle
from src.config import ALL_STOCKS


def _bundle(tmp_path, *, candidate_mae=1.0, baseline_mae=2.0):
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    summary = {}
    for ticker in ALL_STOCKS:
        metrics = {"mae": candidate_mae}
        summary[ticker] = {
            "model_name": "LinearRegression",
            "model_version": "test-version",
            "test_metrics": metrics,
            "naive_baseline_metrics": {"mae": baseline_mae},
        }
        joblib.dump(
            {"ticker": ticker, "test_metrics": metrics},
            models_dir / f"{ticker.replace('.', '_')}.joblib",
        )
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    return summary_path, models_dir


def test_model_bundle_accepts_candidate_within_baseline_ceiling(tmp_path) -> None:
    summary_path, models_dir = _bundle(tmp_path)

    result = validate_model_bundle(summary_path, models_dir)

    assert set(result) == set(ALL_STOCKS)
    assert result["AAPL"]["baseline_mae_ratio"] == 0.5


def test_model_bundle_rejects_candidate_above_baseline_ceiling(tmp_path) -> None:
    summary_path, models_dir = _bundle(
        tmp_path, candidate_mae=4.01, baseline_mae=2.0
    )

    with pytest.raises(ValueError, match="exceeds the 2x last-close baseline ceiling"):
        validate_model_bundle(summary_path, models_dir)


def test_model_bundle_rejects_missing_tickers(tmp_path) -> None:
    summary_path, models_dir = _bundle(tmp_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary.pop("AAPL")
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    with pytest.raises(ValueError, match="Ticker coverage mismatch"):
        validate_model_bundle(summary_path, models_dir)
