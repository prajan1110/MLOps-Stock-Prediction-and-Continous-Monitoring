"""Leak-aware time-series feature engineering."""

import pandas as pd

from src.validation import validate_ohlcv

NUM_LAGS = 10
ROLLING_WINDOWS = (5, 10, 20, 50)
FEATURE_COLUMNS = tuple(
    [f"close_lag_{lag}" for lag in range(1, NUM_LAGS + 1)]
    + [f"close_ma_{window}" for window in ROLLING_WINDOWS]
    + ["rsi_14", "bb_middle_20", "bb_upper_20", "bb_lower_20", "volume_ma_20"]
)


def _features_for_symbol(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.sort_values("date").copy()
    close = result["close"]

    for lag in range(1, NUM_LAGS + 1):
        result[f"close_lag_{lag}"] = close.shift(lag)
    for window in ROLLING_WINDOWS:
        result[f"close_ma_{window}"] = close.rolling(window, min_periods=window).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=14).mean()
    loss = -delta.clip(upper=0).rolling(14, min_periods=14).mean()
    relative_strength = gain / loss.replace(0, float("nan"))
    result["rsi_14"] = 100 - (100 / (1 + relative_strength))
    result.loc[(loss == 0) & (gain > 0), "rsi_14"] = 100.0

    middle = close.rolling(20, min_periods=20).mean()
    deviation = close.rolling(20, min_periods=20).std()
    result["bb_middle_20"] = middle
    result["bb_upper_20"] = middle + 2 * deviation
    result["bb_lower_20"] = middle - 2 * deviation
    result["volume_ma_20"] = result["volume"].rolling(20, min_periods=20).mean()

    result["target"] = close.shift(-1)
    result["target_time"] = result["date"].shift(-1)
    return result


def build_features(data: pd.DataFrame) -> pd.DataFrame:
    """Build rolling features and next-period targets independently per symbol."""
    normalized = validate_ohlcv(data)
    parts = [_features_for_symbol(group) for _, group in normalized.groupby("symbol", sort=False)]
    featured = pd.concat(parts, ignore_index=True)
    return featured.dropna(subset=[*FEATURE_COLUMNS, "target", "target_time"]).sort_values(
        ["symbol", "date"], kind="stable"
    ).reset_index(drop=True)