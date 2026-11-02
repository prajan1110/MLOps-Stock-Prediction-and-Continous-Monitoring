import pandas as pd
import pytest

from src.features import FEATURE_COLUMNS, build_features
from src.preprocessing import preprocess_ohlcv
from src.data_collection import normalize_history
from src.train import split_chronologically


def sample_ohlcv(rows: int = 80) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=rows, freq="h", tz="UTC")
    values = range(100, 100 + rows)
    return pd.DataFrame(
        {
            "date": dates,
            "symbol": "TEST",
            "open": values,
            "high": [value + 1 for value in values],
            "low": [value - 1 for value in values],
            "close": values,
            "volume": [1000] * rows,
        }
    )


def test_preprocessing_normalizes_timezone_and_order() -> None:
    data = sample_ohlcv().sample(frac=1, random_state=4)

    processed = preprocess_ohlcv(data)

    assert processed["date"].is_monotonic_increasing
    assert str(processed["date"].dt.tz) == "UTC"


def test_validation_rejects_duplicate_symbol_timestamps() -> None:
    data = sample_ohlcv()
    data = pd.concat([data, data.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate"):
        preprocess_ohlcv(data)


def test_features_are_per_symbol_and_target_is_future_close() -> None:
    first = sample_ohlcv()
    second = sample_ohlcv().assign(
        symbol="OTHER",
        close=lambda frame: frame["close"] + 100,
        high=lambda frame: frame["high"] + 100,
        low=lambda frame: frame["low"] + 100,
        open=lambda frame: frame["open"] + 100,
    )
    featured = build_features(pd.concat([first, second], ignore_index=True))

    assert set(FEATURE_COLUMNS).issubset(featured.columns)
    assert (featured["target_time"] > featured["date"]).all()
    for _, symbol_rows in featured.groupby("symbol"):
        assert (symbol_rows["target"].iloc[:-1].to_numpy() == symbol_rows["close"].iloc[1:].to_numpy()).all()


def test_yfinance_history_is_normalized_to_ohlcv_schema() -> None:
    history = sample_ohlcv().set_index("date").drop(columns="symbol")
    normalized = normalize_history(history, "test")

    assert list(normalized.columns) == ["date", "symbol", "open", "high", "low", "close", "volume"]
    assert normalized["symbol"].eq("TEST").all()


def test_splits_are_chronological_without_target_overlap() -> None:
    featured = build_features(sample_ohlcv(180))

    splits = split_chronologically(featured)

    assert splits["train"]["date"].max() < splits["validation"]["date"].min()
    assert splits["validation"]["date"].max() < splits["test"]["date"].min()
    assert splits["train"]["target_time"].max() <= splits["validation"]["date"].min()
    assert splits["validation"]["target_time"].max() <= splits["test"]["date"].min()