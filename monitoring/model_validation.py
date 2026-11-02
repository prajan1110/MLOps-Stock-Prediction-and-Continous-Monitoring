"""Quality gates for candidate model artifacts before promotion."""

import argparse
import json
import math
from pathlib import Path
from typing import Any

import joblib

from src.config import ALL_STOCKS

MAX_BASELINE_MAE_RATIO = 2.0


def validate_model_bundle(
    summary_path: Path,
    models_dir: Path,
) -> dict[str, Any]:
    """Require complete artifacts with test MAE within 2x last-close baseline."""
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expected_tickers = set(ALL_STOCKS)
    if set(summary) != expected_tickers:
        missing = sorted(expected_tickers - set(summary))
        unexpected = sorted(set(summary) - expected_tickers)
        raise ValueError(
            f"Ticker coverage mismatch; missing={missing}, unexpected={unexpected}"
        )

    results: dict[str, Any] = {}
    for ticker in ALL_STOCKS:
        result = summary[ticker]
        test_mae = _finite_metric(result, "test_metrics", "mae", ticker)
        baseline_mae = _finite_metric(
            result, "naive_baseline_metrics", "mae", ticker
        )
        max_allowed_mae = baseline_mae * MAX_BASELINE_MAE_RATIO
        if test_mae > max_allowed_mae:
            raise ValueError(
                f"{ticker} candidate test MAE ({test_mae:.6g}) exceeds the "
                f"{MAX_BASELINE_MAE_RATIO:g}x last-close baseline ceiling "
                f"({max_allowed_mae:.6g}; baseline {baseline_mae:.6g})"
            )

        model_path = models_dir / f"{ticker.replace('.', '_')}.joblib"
        if not model_path.is_file():
            raise ValueError(f"Missing model artifact for {ticker}: {model_path}")
        artifact = joblib.load(model_path)
        if artifact.get("ticker") != ticker:
            raise ValueError(f"Model artifact ticker does not match {ticker}")
        if artifact.get("test_metrics", {}).get("mae") != test_mae:
            raise ValueError(f"Summary and artifact test MAE differ for {ticker}")

        results[ticker] = {
            "test_mae": test_mae,
            "last_close_baseline_mae": baseline_mae,
            "baseline_mae_ratio": test_mae / baseline_mae if baseline_mae else 0.0,
            "model_name": result.get("model_name"),
            "model_version": result.get("model_version"),
        }

    return results


def _finite_metric(
    result: dict[str, Any],
    metric_group: str,
    metric_name: str,
    ticker: str,
) -> float:
    try:
        value = float(result[metric_group][metric_name])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            f"Missing {metric_group}.{metric_name} metric for {ticker}"
        ) from error
    if not math.isfinite(value) or value < 0:
        raise ValueError(
            f"{metric_group}.{metric_name} must be finite and nonnegative for {ticker}"
        )
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path("metrics/summary.json"))
    parser.add_argument("--models-dir", type=Path, default=Path("models"))
    args = parser.parse_args()
    result = validate_model_bundle(args.summary, args.models_dir)
    print(json.dumps({"status": "approved", "tickers": result}, indent=2))


if __name__ == "__main__":
    main()
