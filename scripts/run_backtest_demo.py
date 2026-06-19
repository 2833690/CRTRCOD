from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import polars as pl
from packages.backtesting.metrics import compute_metrics
from packages.backtesting.report_generator import ReportGenerator
from packages.common.types import OrderSide, Trade
from packages.strategies.vwap_mean_reversion import VWAPMeanReversion
from scripts.create_sample_data import main as create_sample_data


def run_demo() -> dict:
    path = Path("data/raw/binance/BTC_USDT/5m/sample.parquet")
    if not path.exists():
        create_sample_data()
    df = pl.read_parquet(path)
    strategy = VWAPMeanReversion()
    signals = strategy.run(df)
    trades: list[Trade] = []
    for row in signals.filter(pl.col("entry_long")).head(10).iter_rows(named=True):
        entry = float(row["close"])
        exit_price = entry * 1.002
        gross = exit_price - entry
        fees = (entry + exit_price) * 0.001
        trades.append(Trade(datetime.now(UTC), datetime.now(UTC), "BTC/USDT", OrderSide.BUY, 1.0, entry, exit_price, gross, fees, 0.0, gross - fees))
    equity = [10000 + sum(t.net_pnl for t in trades[:i]) for i in range(len(trades)+1)]
    return compute_metrics(trades, equity)


def main() -> None:
    metrics = run_demo()
    print(ReportGenerator().to_markdown(metrics))

if __name__ == "__main__":
    main()
