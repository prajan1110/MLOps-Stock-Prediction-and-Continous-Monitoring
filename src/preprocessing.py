"""Preprocessing helpers and command-line dataset normalization."""

import argparse
from pathlib import Path

import pandas as pd

from src.validation import validate_ohlcv


def preprocess_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize OHLCV data before feature generation."""
    return validate_ohlcv(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and normalize OHLCV data")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    processed = preprocess_ohlcv(pd.read_csv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(args.output, index=False)
    print(f"Validated {len(processed)} rows -> {args.output}")


if __name__ == "__main__":
    main()