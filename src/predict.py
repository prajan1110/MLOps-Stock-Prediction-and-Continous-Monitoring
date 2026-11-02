"""Load versioned model artifacts and validate feature-payload predictions."""

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


def load_model_artifact(ticker: str, models_dir: Path = Path("models")) -> dict[str, Any]:
    """Load a ticker's selected artifact or report that it has not been trained."""
    path = models_dir / f"{ticker.upper().replace('.', '_')}.joblib"
    if not path.is_file():
        raise FileNotFoundError(f"No trained model for {ticker.upper()} at {path}")
    artifact = joblib.load(path)
    if artifact.get("ticker") != ticker.upper():
        raise ValueError(f"Model artifact ticker does not match {ticker.upper()}")
    return artifact


def predict_from_features(
    artifact: dict[str, Any], features: dict[str, float]
) -> float:
    """Predict one target close from a complete, finite feature mapping."""
    feature_columns = artifact["feature_columns"]
    missing = [column for column in feature_columns if column not in features]
    if missing:
        raise ValueError(f"Missing model features: {', '.join(missing)}")
    values = pd.DataFrame([[features[column] for column in feature_columns]], columns=feature_columns)
    if not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError("Features must contain only finite numbers")
    prediction = artifact["model"].predict(values)
    return float(prediction[0])