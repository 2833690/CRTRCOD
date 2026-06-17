from dataclasses import dataclass
from datetime import datetime
from time import perf_counter

from packages.common.types import OrderSide, RiskDecision

from .kill_switch import KillSwitch
from .limits import RiskLimits


@dataclass
class OrderRequest:
    strategy_id: str
    symbol: str
    side: OrderSide
    order_type: str
    quantity: float
    price: float
    timeframe: str
    signal_ts: datetime


class RiskEngine:
    """Главный предохранитель CRTRCOD.

    Любой paper/live ордер обязан пройти этот класс до исполнения.
    Проверки идут строго fail-fast: как только найдено нарушение, ордер
    получает REJECT или REDUCE, а причина записывается в audit log.
    Такой порядок проще расследовать оператору и безопаснее для live режима.
    """

    def __init__(self, limits: RiskLimits, kill_switch: KillSwitch, db_session=None):
        self.limits = limits
        self.kill_switch = kill_switch
        self.db = db_session

    def _get(self, name, default):
        return getattr(self.db, name, default) if self.db is not None else default

    def _audit(self, order, checks, decision, reason, start):
        if self.db is not None and hasattr(self.db, "audit_log"):
            self.db.audit_log.append(
                {
                    "order_id": id(order),
                    "checks_run": checks,
                    "decision": decision.value,
                    "reason": reason,
                    "latency_ms": (perf_counter() - start) * 1000,
                }
            )

    def validate_order(self, order: OrderRequest) -> tuple[RiskDecision, str]:
        """Проверить ордер и вернуть решение risk layer.

        Returns:
            `(RiskDecision, reason_code)`, где reason_code стабилен для
            алертов, dashboard и автоматических тестов.
        """
        start = perf_counter()
        checks = []

        def finish(dec, reason):
            self._audit(order, checks, dec, reason, start)
            return dec, reason

        checks.append("kill_switch")
        if not self.kill_switch.is_trading_allowed():
            return finish(RiskDecision.REJECT, "kill_switch_active")
        capital = float(self._get("total_capital", 10000))
        checks.append("daily_loss")
        if float(self._get("daily_pnl", 0)) <= -(capital * self.limits.max_daily_loss_pct):
            return finish(RiskDecision.REJECT, "daily_loss_exceeded")
        value = order.quantity * order.price
        limit = capital * self.limits.max_position_size_pct
        checks.append("position_size")
        if value > limit * 1.10:
            return finish(RiskDecision.REJECT, "position_size_too_large")
        if value > limit:
            return finish(RiskDecision.REDUCE, "position_size_reduce")
        checks.append("concurrent_positions")
        if int(self._get("open_positions", 0)) >= self.limits.max_concurrent_positions:
            return finish(RiskDecision.REJECT, "too_many_positions")
        checks.append("spread")
        if float(self._get("spread_bps", 0)) > self.limits.max_spread_bps:
            return finish(RiskDecision.REJECT, "spread_too_wide")
        checks.append("data_freshness")
        if bool(self._get("stale_data", False)):
            return finish(RiskDecision.REJECT, "stale_data")
        return finish(RiskDecision.ALLOW, "ok")
