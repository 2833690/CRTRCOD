from datetime import UTC, datetime, timedelta

import polars as pl

from packages.common.types import OrderSide, RiskDecision
from packages.risk.engine import OrderRequest


class PaperTrader:
    def __init__(self, strategy, risk_engine, fill_simulator, db_session=None):
        self.strategy = strategy
        self.risk_engine = risk_engine
        self.fill_simulator = fill_simulator
        self.db = db_session
        self.candles = []
        self.events = []

    def on_candle(self, candle: dict) -> None:
        self.candles.append(candle)
        df = pl.DataFrame(self.candles)
        df = self.strategy.populate_entry_signal(self.strategy.populate_indicators(df))
        row = df.row(-1, named=True)
        if row.get("entry_long"):
            order = OrderRequest(
                self.strategy.strategy_id,
                row.get("symbol", "BTC/USDT"),
                OrderSide.BUY,
                "limit",
                1,
                row["close"],
                self.strategy.timeframe,
                datetime.now(UTC),
            )
            dec, _ = self.risk_engine.validate_order(order)
            if dec == RiskDecision.ALLOW:
                self.events.append(
                    self.fill_simulator.simulate_fill(
                        row["close"], OrderSide.BUY, row.get("spread_bps", 0), 0.0005
                    )
                )

    def get_daily_summary(self) -> dict:
        return {"daily_pnl": 0.0, "fill_quality": 0.0, "signal_count": len(self.events)}

    def check_data_freshness(self, last_candle_ts: datetime, timeframe: str) -> bool:
        return datetime.now(UTC) - last_candle_ts < timedelta(minutes=10)
