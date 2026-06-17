from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    max_capital_per_strategy_pct: float = 0.05
    max_risk_per_trade_pct: float = 0.0025
    max_daily_loss_pct: float = 0.01
    max_concurrent_positions: int = 2
    max_position_size_pct: float = 0.03
    max_spread_bps: float = 5.0
    max_consecutive_losses: int = 5
    data_staleness_multiplier: float = 2.0
