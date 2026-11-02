"""Validation for raw and prepared OHLCV datasets."""

import pandas as pd

REQUIRED_COLUMNS = ("date", "symbol", "open", "high", "low", "close", "volume")
PRICE_COLUMNS = ("open", "high", "low", "close")


def validate_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    """Return a sorted, normalized OHLCV frame or raise a useful error."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("OHLCV data must be a pandas DataFrame")
    if data.empty:
        raise ValueError("OHLCV data is empty")

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"OHLCV data is missing columns: {', '.join(missing)}")

    frame = data.loc[:, list(REQUIRED_COLUMNS)].copy()
    frame["date"] = pd.to_datetime(frame["date"], utc=True, errors="coerce")
    if frame["date"].isna().any():
        raise ValueError("OHLCV data contains invalid timestamps")

    frame["symbol"] = frame["symbol"].astype("string").str.strip().str.upper()
    if frame["symbol"].isna().any() or frame["symbol"].eq("").any():
        raise ValueError("OHLCV data contains an empty symbol")

    for column in (*PRICE_COLUMNS, "volume"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame[[*PRICE_COLUMNS, "volume"]].isna().any().any():
        raise ValueError("OHLCV data contains missing or non-numeric prices/volume")
    if (frame[list(PRICE_COLUMNS)] <= 0).any().any():
        raise ValueError("OHLCV prices must be greater than zero")
    if (frame["volume"] < 0).any():
        raise ValueError("OHLCV volume cannot be negative")
    if (frame["high"] < frame["low"]).any():
        raise ValueError("OHLCV high cannot be lower than low")
    if (frame["high"] < frame[["open", "close"]].max(axis=1)).any():
        raise ValueError("OHLCV high must be at least open and close")
    if (frame["low"] > frame[["open", "close"]].min(axis=1)).any():
        raise ValueError("OHLCV low must be no greater than open and close")
    if frame.duplicated(["date", "symbol"]).any():
        raise ValueError("OHLCV data contains duplicate date/symbol rows")

    return frame.sort_values(["symbol", "date"], kind="stable").reset_index(drop=True)