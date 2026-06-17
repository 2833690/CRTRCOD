import numpy as np


class LookaheadBiasDetected(Exception):
    pass


def test_no_lookahead(strategy_fn, df):
    shuffled = df.sample(fraction=1.0, shuffle=True, seed=42)
    out = strategy_fn(shuffled)
    sig = np.array(
        out.get_column("entry_long") if "entry_long" in out.columns else [0] * len(out), dtype=float
    )
    ret = np.array(out.get_column("close").pct_change().fill_null(0), dtype=float)
    pnl = sig * ret
    sharpe = float(pnl.mean() / (pnl.std() or 1) * np.sqrt(252))
    if sharpe > 0.5:
        raise LookaheadBiasDetected(sharpe)
    return abs(sharpe) < 0.3
