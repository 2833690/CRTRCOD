import polars as pl

from packages.backtesting.metrics import compute_metrics


def test_backtest_reproducibility():
    trades = pl.DataFrame(
        {
            "net_pnl": [1.0, -0.5],
            "gross_pnl": [1.1, -0.4],
            "fees": [0.1, 0.1],
            "slippage": [0.0, 0.0],
        }
    )
    eq = pl.DataFrame({"equity": [100, 101, 100.5]})
    assert compute_metrics(trades, eq) == compute_metrics(trades, eq)
