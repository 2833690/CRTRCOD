from datetime import UTC, datetime, timedelta

import numpy as np
import polars as pl
import pytest
from packages.common.types import KillSwitchState
from packages.risk.kill_switch import KillSwitch


@pytest.fixture
def sample_ohlcv_df():
    rng = np.random.default_rng(42)
    n = 240
    base = 100 + np.cumsum(rng.normal(0, 0.2, n))
    return pl.DataFrame({
        "timestamp": [datetime(2024,1,1,tzinfo=UTC)+timedelta(minutes=5*i) for i in range(n)],
        "open": base,
        "high": base + 1,
        "low": base - 1,
        "close": base + rng.normal(0, 0.1, n),
        "volume": rng.uniform(100, 200, n),
        "bid": base - 0.01,
        "ask": base + 0.01,
    })

@pytest.fixture
def mock_kill_switch():
    ks = KillSwitch()
    ks.set_state(KillSwitchState.ACTIVE, "test", "active")
    return ks
