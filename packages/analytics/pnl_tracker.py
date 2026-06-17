import polars as pl


class PnLTracker:
    def get_daily_pnl(self, strategy_id=None, days=30):
        return pl.DataFrame({"date": [], "pnl": []})

    def get_cumulative_pnl(self, strategy_id):
        return pl.DataFrame({"ts": [], "pnl": []})

    def get_fee_breakdown(self, strategy_id, days=7):
        return {"maker": 0.0, "taker": 0.0}
