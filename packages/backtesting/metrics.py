from __future__ import annotations

import itertools
from dataclasses import asdict, is_dataclass

import numpy as np


def _values(rows, name: str) -> np.ndarray:
    if rows is None:
        return np.array([])
    if isinstance(rows, dict) and name in rows:
        return np.asarray(rows[name], dtype=float)
    if hasattr(rows, "columns") and name in rows.columns:
        return np.asarray(rows[name], dtype=float)
    vals = []
    for row in rows:
        if is_dataclass(row):
            row = asdict(row)  # type: ignore[arg-type]
        vals.append(row.get(name, 0) if isinstance(row, dict) else getattr(row, name, 0))
    return np.asarray(vals, dtype=float)


def compute_metrics(trades, equity_curve) -> dict[str, float | int | None]:
    pnl = _values(trades, "net_pnl")
    gross = _values(trades, "gross_pnl")
    fees = _values(trades, "fees")
    slip = _values(trades, "slippage")
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    equity = np.asarray(equity_curve, dtype=float) if not hasattr(equity_curve, "columns") else _values(equity_curve, "equity")
    dd = equity / np.maximum.accumulate(equity) - 1 if equity.size else np.array([0.0])
    downside = losses.std() if losses.size else 0.0
    return {
        "net_pnl": float(pnl.sum() if pnl.size else 0),
        "gross_pnl": float(gross.sum() if gross.size else 0),
        "total_fees": float(fees.sum() if fees.size else 0),
        "total_slippage": float(slip.sum() if slip.size else 0),
        "win_rate": float(len(wins) / len(pnl) if len(pnl) else 0),
        "profit_factor": float(wins.sum() / abs(losses.sum()) if losses.size and losses.sum() else 0),
        "expectancy": float(pnl.mean() if pnl.size else 0),
        "sharpe": float(pnl.mean() / (pnl.std() or 1) if pnl.size else 0),
        "sortino": float(pnl.mean() / (downside or 1) if pnl.size else 0),
        "max_drawdown_pct": float(dd.min() * 100),
        "num_trades": int(len(pnl)),
        "max_consecutive_losses": int(max((len(list(g)) for k, g in itertools.groupby(pnl < 0) if k), default=0)),
        "risk_of_ruin_pct": float(max(0.0, min(100.0, (1 - (len(wins) / len(pnl))) * 10)) if len(pnl) else 0),
    }
