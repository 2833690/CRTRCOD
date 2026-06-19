from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import polars as pl


def make_sample_data(rows: int = 2000) -> pl.DataFrame:
    rng = np.random.default_rng(42)
    returns = rng.normal(0.00005, 0.002, rows)
    close = 50000 * np.cumprod(1 + returns)
    open_ = np.concatenate(([close[0]], close[:-1]))
    spread = rng.uniform(5, 80, rows)
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread
    volume = rng.uniform(20, 200, rows)
    start = datetime(2024, 1, 1, tzinfo=UTC)
    return pl.DataFrame({
        "timestamp": [start + timedelta(minutes=5*i) for i in range(rows)],
        "open": open_, "high": high, "low": low, "close": close, "volume": volume,
        "symbol": ["BTC/USDT"] * rows, "timeframe": ["5m"] * rows, "exchange": ["binance"] * rows,
    })


def main() -> None:
    path = Path("data/raw/binance/BTC_USDT/5m/sample.parquet")
    path.parent.mkdir(parents=True, exist_ok=True)
    make_sample_data().write_parquet(path)
    print(f"Wrote {path}")

if __name__ == "__main__":
    main()
