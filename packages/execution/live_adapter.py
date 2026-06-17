from packages.common.types import RiskDecision


class LiveTradingNotEnabled(RuntimeError):
    pass


class LiveAdapter:
    def __init__(self, ccxt_client, risk_engine, db_session=None):
        self.ccxt_client = ccxt_client
        self.risk_engine = risk_engine
        self.db = db_session

    def is_live_trading_enabled(self) -> bool:
        return (
            bool(getattr(self.db, "live_enabled", False))
            and self.risk_engine.kill_switch.is_trading_allowed()
        )

    def place_order(self, order):
        if not self.is_live_trading_enabled():
            raise LiveTradingNotEnabled("Live trading disabled")
        decision, reason = self.risk_engine.validate_order(order)
        if decision == RiskDecision.REJECT:
            raise RuntimeError(reason)
        return {
            "status": "placed",
            "symbol": order.symbol,
            "quantity": order.quantity,
            "price": order.price,
        }
