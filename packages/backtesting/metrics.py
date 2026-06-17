import numpy as np


def _col(df, name):
    return np.array(df[name]) if name in df.columns else np.array([])


def compute_metrics(trades, equity_curve):
    pnl = _col(trades, "net_pnl")
    gross = _col(trades, "gross_pnl")
    fees = _col(trades, "fees")
    slip = _col(trades, "slippage")
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    equity = _col(equity_curve, "equity")
    dd = (equity / np.maximum.accumulate(equity) - 1) if equity.size else np.array([0])
    return {
        "net_pnl": float(pnl.sum() if pnl.size else 0),
        "gross_pnl": float(gross.sum() if gross.size else pnl.sum() if pnl.size else 0),
        "total_fees": float(fees.sum() if fees.size else 0),
        "total_slippage": float(slip.sum() if slip.size else 0),
        "fee_impact_pct": 0.0,
        "win_rate": float(len(wins) / len(pnl) if len(pnl) else 0),
        "profit_factor": float(
            wins.sum() / abs(losses.sum()) if losses.size and losses.sum() != 0 else 0
        ),
        "expectancy_per_trade": float(pnl.mean() if pnl.size else 0),
        "sharpe_ratio": float(
            pnl.mean() / (pnl.std() or 1) * np.sqrt(252 * 24 * 12) if pnl.size else 0
        ),
        "sortino_ratio": 0.0,
        "max_drawdown_pct": float(dd.min() * 100),
        "max_drawdown_duration_days": 0.0,
        "avg_trade_pnl": float(pnl.mean() if pnl.size else 0),
        "avg_hold_time_minutes": 0.0,
        "num_trades": int(len(pnl)),
        "daily_pnl_mean": float(pnl.mean() if pnl.size else 0),
        "daily_pnl_std": float(pnl.std() if pnl.size else 0),
        "daily_pnl_skew": 0.0,
        "max_consecutive_losses": int(
            max((len(list(g)) for k, g in __import__("itertools").groupby(pnl < 0) if k), default=0)
        ),
        "risk_of_ruin_pct": 0.0,
    }
