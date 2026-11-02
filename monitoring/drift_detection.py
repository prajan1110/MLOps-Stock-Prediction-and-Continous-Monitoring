"""Population Stability Index checks for numeric feature drift."""

import argparse
import json
import logging
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def population_stability_index(
    reference: Sequence[float], current: Sequence[float], bins: int = 10
) -> float:
    """Calculate PSI using reference quantile bins for two finite samples."""
    if bins < 2:
        raise ValueError("bins must be at least 2")
    reference_values = np.asarray(reference, dtype=float)
    current_values = np.asarray(current, dtype=float)
    reference_values = reference_values[np.isfinite(reference_values)]
    current_values = current_values[np.isfinite(current_values)]
    if reference_values.size < 2 or current_values.size < 2:
        raise ValueError("Reference and current samples must each contain at least two finite values")

    edges = np.unique(np.quantile(reference_values, np.linspace(0, 1, bins + 1)))
    if edges.size < 2:
        edges = np.array([reference_values[0] - 0.5, reference_values[0] + 0.5])
    edges[0] = -np.inf
    edges[-1] = np.inf
    reference_counts = np.histogram(reference_values, bins=edges)[0]
    current_counts = np.histogram(current_values, bins=edges)[0]
    epsilon = 1e-6
    expected = np.maximum(reference_counts / reference_values.size, epsilon)
    actual = np.maximum(current_counts / current_values.size, epsilon)
    return float(np.sum((actual - expected) * np.log(actual / expected)))


def compare_feature_distributions(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    threshold: float = 0.2,
) -> dict[str, dict[str, float | bool]]:
    """Calculate PSI for shared numeric columns and flag threshold breaches."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    columns = [
        column
        for column in reference.select_dtypes(include="number").columns
        if column in current.columns and pd.api.types.is_numeric_dtype(current[column])
    ]
    if not columns:
        raise ValueError("No shared numeric feature columns to compare")

    results = {}
    for column in columns:
        psi = population_stability_index(reference[column], current[column])
        drift = psi >= threshold
        results[column] = {"psi": psi, "drift": drift}
        if drift:
            logger.warning("Feature drift detected feature=%s psi=%.4f threshold=%.4f", column, psi, threshold)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare feature distributions for drift")
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.2)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    results = compare_feature_distributions(
        pd.read_csv(args.reference), pd.read_csv(args.current), args.threshold
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()