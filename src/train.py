"""Chronological model comparison, tracking, and artifact packaging."""

import argparse
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from src.evaluate import regression_metrics
from src.features import FEATURE_COLUMNS, build_features
from src.preprocessing import preprocess_ohlcv

logger = logging.getLogger(__name__)
EXPERIMENT_NAME = "stock-price-prediction"
TARGET_DEFINITION = "next-observation close from current OHLCV-derived features"


def split_chronologically(
    frame: pd.DataFrame,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
) -> dict[str, pd.DataFrame]:
    """Split one ticker's feature frame in time order; keep the test set untouched."""
    if not 0 < train_ratio < 1 or not 0 < validation_ratio < 1:
        raise ValueError("Split ratios must be between zero and one")
    if train_ratio + validation_ratio >= 1:
        raise ValueError("Train and validation ratios must leave data for testing")

    ordered = frame.sort_values("date", kind="stable").reset_index(drop=True)
    train_end = int(len(ordered) * train_ratio)
    validation_end = train_end + int(len(ordered) * validation_ratio)
    if train_end < 2 or validation_end <= train_end or validation_end >= len(ordered):
        raise ValueError("Not enough rows for chronological train/validation/test splits")

    splits = {
        "train": ordered.iloc[:train_end].copy(),
        "validation": ordered.iloc[train_end:validation_end].copy(),
        "test": ordered.iloc[validation_end:].copy(),
    }
    if not (
        splits["train"]["target_time"].max() <= splits["validation"]["date"].min()
        and splits["validation"]["target_time"].max() <= splits["test"]["date"].min()
    ):
        raise ValueError("Time split overlaps a target across partitions")
    return splits


def _dataset_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as dataset_file:
        for chunk in iter(lambda: dataset_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _model_candidates() -> dict[str, Any]:
    return {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=1),
    }


def train_dataset(
    input_path: Path,
    models_dir: Path = Path("models"),
    tracking_uri: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Train and track both estimators per ticker, then package the selected model."""
    load_dotenv()
    input_path = input_path.resolve()
    models_dir.mkdir(parents=True, exist_ok=True)
    dataset_hash = _dataset_digest(input_path)
    tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI") or Path("mlruns").resolve().as_uri()
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    raw_data = pd.read_csv(input_path)
    normalized = preprocess_ohlcv(raw_data)
    featured = build_features(normalized)
    results: dict[str, dict[str, Any]] = {}

    for ticker, ticker_frame in featured.groupby("symbol", sort=True):
        splits = split_chronologically(ticker_frame)
        train_frame = splits["train"]
        validation_frame = splits["validation"]
        test_frame = splits["test"]
        x_train = train_frame.loc[:, FEATURE_COLUMNS]
        y_train = train_frame["target"]
        x_validation = validation_frame.loc[:, FEATURE_COLUMNS]
        y_validation = validation_frame["target"]
        candidates: dict[str, tuple[Any, dict[str, float]]] = {}

        with mlflow.start_run(run_name=f"{ticker}-comparison") as run:
            mlflow.log_params(
                {
                    "ticker": ticker,
                    "target": TARGET_DEFINITION,
                    "dataset_sha256": dataset_hash,
                    "train_rows": len(train_frame),
                    "validation_rows": len(validation_frame),
                    "test_rows": len(test_frame),
                    "selection_metric": "validation_mae",
                }
            )
            mlflow.log_dict({"feature_columns": list(FEATURE_COLUMNS)}, "feature_schema.json")

            for model_name, estimator in _model_candidates().items():
                with mlflow.start_run(run_name=model_name, nested=True):
                    estimator.fit(x_train, y_train)
                    validation_metrics = regression_metrics(
                        y_validation, estimator.predict(x_validation)
                    )
                    mlflow.log_param("model_name", model_name)
                    mlflow.log_metrics({f"validation_{key}": value for key, value in validation_metrics.items()})
                    candidates[model_name] = (estimator, validation_metrics)

            selected_name = min(candidates, key=lambda name: candidates[name][1]["mae"])
            selected_model, selected_validation = candidates[selected_name]

            x_train_validation = pd.concat([x_train, x_validation], axis=0)
            y_train_validation = pd.concat([y_train, y_validation], axis=0)
            selected_model.fit(x_train_validation, y_train_validation)
            test_metrics = regression_metrics(
                test_frame["target"], selected_model.predict(test_frame.loc[:, FEATURE_COLUMNS])
            )
            naive_baseline_metrics = regression_metrics(
                test_frame["target"], test_frame["close"]
            )
            mlflow.log_param("selected_model", selected_name)
            mlflow.log_metrics({f"test_{key}": value for key, value in test_metrics.items()})
            mlflow.log_metrics(
                {
                    f"naive_baseline_test_{key}": value
                    for key, value in naive_baseline_metrics.items()
                }
            )
            mlflow.log_metrics(
                {f"selected_validation_{key}": value for key, value in selected_validation.items()}
            )

            trained_at = datetime.now(timezone.utc).isoformat()
            artifact = {
                "model": selected_model,
                "ticker": ticker,
                "model_name": selected_name,
                "model_version": run.info.run_id,
                "trained_at": trained_at,
                "dataset_sha256": dataset_hash,
                "target_definition": TARGET_DEFINITION,
                "feature_columns": list(FEATURE_COLUMNS),
                "validation_metrics": selected_validation,
                "test_metrics": test_metrics,
                "naive_baseline_metrics": naive_baseline_metrics,
                "test_start": test_frame["date"].min().isoformat(),
                "test_end": test_frame["target_time"].max().isoformat(),
            }
            artifact_path = models_dir / f"{ticker.replace('.', '_')}.joblib"
            joblib.dump(artifact, artifact_path)
            mlflow.log_artifact(str(artifact_path), artifact_path="selected_model")

        results[ticker] = {
            "model_name": selected_name,
            "model_version": run.info.run_id,
            "artifact_path": str(artifact_path),
            "validation_metrics": selected_validation,
            "test_metrics": test_metrics,
            "naive_baseline_metrics": naive_baseline_metrics,
        }
        logger.info(
            "%s selected %s; test MAE %.4f, RMSE %.4f",
            ticker,
            selected_name,
            test_metrics["mae"],
            test_metrics["rmse"],
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and track stock prediction models")
    parser.add_argument("--input", type=Path, default=Path("data/processed/training.csv"))
    parser.add_argument("--models-dir", type=Path, default=Path("models"))
    parser.add_argument("--tracking-uri", default=None)
    parser.add_argument("--metrics-output", type=Path, default=Path("metrics/summary.json"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    results = train_dataset(args.input, args.models_dir, args.tracking_uri)
    args.metrics_output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()