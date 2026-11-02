"""Collect a reproducible daily OHLCV dataset from Yahoo Finance."""

import argparse
import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

from src.config import ALL_STOCKS
from src.validation import REQUIRED_COLUMNS, validate_ohlcv

logger = logging.getLogger(__name__)


def normalize_history(history: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Normalize one yfinance history frame into the project's OHLCV schema."""
    if history.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    frame = history.reset_index()
    datetime_column = next(
        (column for column in ("Datetime", "Date", "index") if column in frame.columns),
        frame.columns[0],
    )
    columns = {str(column).lower(): column for column in frame.columns}
    required = {name: columns.get(name) for name in ("open", "high", "low", "close", "volume")}
    missing = [name for name, source in required.items() if source is None]
    if missing:
        raise ValueError(f"Yahoo Finance response for {symbol} is missing: {', '.join(missing)}")

    normalized = frame[[datetime_column, *required.values()]].copy()
    normalized.columns = ["date", *required.keys()]
    normalized["symbol"] = symbol.upper()
    return validate_ohlcv(normalized.loc[:, list(REQUIRED_COLUMNS)])


def collect_dataset(
    symbols: tuple[str, ...] = ALL_STOCKS,
    period: str = "2y",
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch, normalize, validate, and combine a daily training dataset."""
    frames = []
    failures = []
    for symbol in symbols:
        try:
            history = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=False)
            normalized = normalize_history(history, symbol)
            if normalized.empty:
                failures.append(symbol)
            else:
                frames.append(normalized)
        except Exception:
            logger.exception("Failed to collect %s", symbol)
            failures.append(symbol)

    if not frames:
        raise RuntimeError("No valid stock data was collected")
    if failures:
        logger.warning("No usable history for: %s", ", ".join(failures))
    return validate_ohlcv(pd.concat(frames, ignore_index=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect validated OHLCV training data")
    parser.add_argument("--output", type=Path, default=Path("data/raw/stock_data.csv"))
    parser.add_argument("--period", default="2y")
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--symbols", default=",".join(ALL_STOCKS))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    symbols = tuple(symbol.strip().upper() for symbol in args.symbols.split(",") if symbol.strip())
    dataset = collect_dataset(symbols, args.period, args.interval)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output, index=False)
    print(f"Collected {len(dataset)} rows for {dataset['symbol'].nunique()} symbols -> {args.output}")


if __name__ == "__main__":
    main()