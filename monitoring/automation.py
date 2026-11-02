"""Scheduled data refresh, feature-drift checks, and conditional retraining."""

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

from monitoring.drift_detection import compare_feature_distributions
from src.config import ALL_STOCKS
from src.features import FEATURE_COLUMNS, build_features
from src.preprocessing import preprocess_ohlcv

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_SNAPSHOT_COLUMNS = ("symbol", *FEATURE_COLUMNS)


def build_feature_snapshot(data: pd.DataFrame) -> pd.DataFrame:
    """Create the numeric feature rows used for baseline and current comparisons."""
    featured = build_features(preprocess_ohlcv(data))
    missing_symbols = sorted(set(ALL_STOCKS) - set(featured["symbol"]))
    if missing_symbols:
        raise ValueError(f"Dataset is missing supported tickers: {', '.join(missing_symbols)}")
    return featured.loc[:, list(FEATURE_SNAPSHOT_COLUMNS)].reset_index(drop=True)


def compare_snapshots(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    threshold: float = 0.2,
) -> dict[str, dict[str, dict[str, float | bool]]]:
    """Compare matching numeric feature distributions separately for each ticker."""
    if "symbol" not in reference or "symbol" not in current:
        raise ValueError("Feature snapshots must contain a symbol column")

    report: dict[str, dict[str, dict[str, float | bool]]] = {}
    for ticker in sorted(set(reference["symbol"]) & set(current["symbol"])):
        reference_rows = reference.loc[reference["symbol"] == ticker]
        current_rows = current.loc[current["symbol"] == ticker]
        report[str(ticker)] = compare_feature_distributions(
            reference_rows.drop(columns="symbol"),
            current_rows.drop(columns="symbol"),
            threshold,
        )
    if not report:
        raise ValueError("No matching tickers are available for drift comparison")
    return report


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary_path.replace(path)


def run_cycle(project_root: Path = PROJECT_ROOT, threshold: float = 0.2) -> dict[str, object]:
    """Refresh OHLCV data, monitor drift, and retrain when needed."""
    project_root = project_root.resolve()
    data_dir = project_root / "data"
    processed_path = data_dir / "processed" / "training.csv"
    reference_path = data_dir / "reference_features.csv"
    models_dir = project_root / "models"
    metrics_path = project_root / "metrics" / "drift_latest.json"
    dvc_command = [sys.executable, "-m", "dvc", "repro"]

    subprocess.run(
        [*dvc_command, "--force", "collect", "prepare"],
        cwd=project_root,
        check=True,
    )
    current = build_feature_snapshot(pd.read_csv(processed_path))

    baseline_exists = reference_path.is_file()
    reference = pd.read_csv(reference_path) if baseline_exists else pd.DataFrame()
    report = compare_snapshots(reference, current, threshold) if baseline_exists else {}
    drift_detected = any(
        feature_result["drift"]
        for ticker_result in report.values()
        for feature_result in ticker_result.values()
    )
    expected_models = {
        f"{ticker.replace('.', '_')}.joblib" for ticker in ALL_STOCKS
    }
    available_models = {path.name for path in models_dir.glob("*.joblib")}
    bootstrap_required = not baseline_exists or not expected_models.issubset(available_models)
    retrain = drift_detected or bootstrap_required

    result: dict[str, object] = {
        "threshold": threshold,
        "drift_detected": drift_detected,
        "bootstrap_required": bootstrap_required,
        "retrained": False,
        "tickers": report,
    }
    _write_json(metrics_path, result)

    if retrain:
        logger.info(
            "Starting DVC training pipeline drift_detected=%s bootstrap_required=%s",
            drift_detected,
            bootstrap_required,
        )
        subprocess.run([*dvc_command, "train"], cwd=project_root, check=True)
        missing_models = expected_models - {
            path.name for path in models_dir.glob("*.joblib")
        }
        if missing_models:
            raise RuntimeError(
                f"Training completed without model artifacts: {', '.join(sorted(missing_models))}"
            )
        temporary_path = reference_path.with_suffix(".csv.tmp")
        current.to_csv(temporary_path, index=False)
        temporary_path.replace(reference_path)
        result["retrained"] = True
        _write_json(metrics_path, result)
        logger.info("Training succeeded; drift reference updated")
    else:
        logger.info("No feature drift detected; existing models retained")

    return result


def run_scheduler(interval_hours: float, threshold: float) -> None:
    """Run immediately, then repeat at the configured interval."""
    if interval_hours <= 0:
        raise ValueError("interval-hours must be greater than zero")
    interval_seconds = interval_hours * 60 * 60
    logger.info(
        "Starting MLOps automation interval_hours=%s drift_threshold=%s",
        interval_hours,
        threshold,
    )
    while True:
        try:
            run_cycle(threshold=threshold)
        except Exception:
            logger.exception("MLOps automation cycle failed; retrying next interval")
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Automate data refresh, drift checks, and retraining")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--interval-hours", type=float, default=24.0)
    parser.add_argument("--threshold", type=float, default=0.2)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.once:
        run_cycle(threshold=args.threshold)
    else:
        run_scheduler(args.interval_hours, args.threshold)


if __name__ == "__main__":
    main()
