from datetime import UTC, datetime, timedelta

import polars as pl
import pytest
from packages.strategies.breakout_vol_filter import BreakoutVolFilter
from packages.strategies.volume_spike_pullback import VolumeSpikepullback
from packages.strategies.vwap_mean_reversion import VWAPMeanReversion


def candles():
    n = 200
    ts = [datetime.now(UTC) + timedelta(minutes=5 * i) for i in range(n)]
    close = [100 + i * 0.01 for i in range(n)]
    return pl.DataFrame(
        {
            "timestamp_utc": ts,
            "open": close,
            "high": [x + 1 for x in close],
            "low": [x - 1 for x in close],
            "close": close,
            "volume": [100 + i % 10 for i in range(n)],
            "bid": close,
            "ask": [x + 0.01 for x in close],
        }
    )


@pytest.mark.parametrize("cls", [VWAPMeanReversion, BreakoutVolFilter, VolumeSpikepullback])
def test_strategy_shuffle_sharpe_low(cls):
    s = cls()
    df = s.populate_entry_signal(
        s.populate_indicators(candles().sample(fraction=1.0, shuffle=True, seed=42))
    )
    assert "entry_long" in df.columns
