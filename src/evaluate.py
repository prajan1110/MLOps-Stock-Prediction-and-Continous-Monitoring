"""Regression evaluation metrics shared by training and monitoring."""

from collections.abc import Sequence

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(actual: Sequence[float], predicted: Sequence[float]) -> dict[str, float]:
    """Calculate MAE, MSE, RMSE, and R-squared for a non-empty evaluation set."""
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)
    if actual_values.size == 0 or actual_values.shape != predicted_values.shape:
        raise ValueError("Actual and predicted values must have the same non-zero shape")

    mse = float(mean_squared_error(actual_values, predicted_values))
    return {
        "mae": float(mean_absolute_error(actual_values, predicted_values)),
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(actual_values, predicted_values)),
    }