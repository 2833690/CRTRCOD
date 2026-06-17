from packages.common.types import KillSwitchState


class CircuitBreaker:
    def __init__(self, kill_switch=None, db_session=None):
        self.kill_switch = kill_switch
        self.db = db_session

    def check_consecutive_losses(self, strategy_id: str) -> tuple[bool, int]:
        count = getattr(self.db, "consecutive_losses", 0)
        return count >= 5, count

    def check_slippage_anomaly(self, strategy_id: str, window: int = 3) -> bool:
        return False

    def check_data_feed(self, symbol: str, timeframe: str) -> bool:
        return bool(getattr(self.db, "stale_data", False))

    def trigger(self, strategy_id: str, reason: str) -> None:
        if self.kill_switch:
            self.kill_switch.set_state(KillSwitchState.PAUSED, "circuit_breaker", reason)
