import numpy as np
import pandas as pd
import pytest

from monitoring.automation import compare_snapshots
from monitoring.drift_detection import compare_feature_distributions, population_stability_index


def test_psi_is_low_for_stable_distribution() -> None:
    reference = np.linspace(0, 1, 200)

    assert population_stability_index(reference, reference) < 0.01


def test_psi_flags_shifted_feature() -> None:
    reference = np.linspace(0, 1, 200)
    current = reference + 3

    result = compare_feature_distributions(
        pd.DataFrame({"close": reference}), pd.DataFrame({"close": current})
    )

    assert result["close"]["drift"] is True


def test_snapshot_comparison_keeps_tickers_separate() -> None:
    reference = pd.DataFrame(
        {"symbol": ["AAPL"] * 100 + ["MSFT"] * 100, "close": [0.0] * 100 + [100.0] * 100}
    )
    current = pd.DataFrame(
        {"symbol": ["AAPL"] * 100 + ["MSFT"] * 100, "close": [0.0] * 100 + [100.0] * 100}
    )

    report = compare_snapshots(reference, current)

    assert set(report) == {"AAPL", "MSFT"}
    assert report["AAPL"]["close"]["psi"] < 0.01
    assert report["MSFT"]["close"]["psi"] < 0.01


def test_snapshot_comparison_rejects_mismatched_symbols() -> None:
    reference = pd.DataFrame({"symbol": ["AAPL"] * 2, "close": [1.0, 2.0]})
    current = pd.DataFrame({"symbol": ["MSFT"] * 2, "close": [1.0, 2.0]})

    with pytest.raises(ValueError, match="matching tickers"):
        compare_snapshots(reference, current)