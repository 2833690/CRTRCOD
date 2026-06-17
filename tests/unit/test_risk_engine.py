from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from packages.common.types import KillSwitchState, OrderSide, RiskDecision
from packages.risk.engine import OrderRequest, RiskEngine
from packages.risk.kill_switch import KillSwitch
from packages.risk.limits import RiskLimits


class DB(SimpleNamespace):
    def __init__(self, **kw):
        super().__init__(
            audit_log=[],
            total_capital=10000,
            daily_pnl=0,
            open_positions=0,
            spread_bps=1,
            stale_data=False,
            **kw,
        )


@pytest.fixture
def order():
    return OrderRequest(
        "s", "BTC/USDT", OrderSide.BUY, "limit", 0.01, 10000, "5m", datetime.now(UTC)
    )


def engine(db):
    return RiskEngine(RiskLimits(), KillSwitch(db_session=db), db)


def test_kill_switch_paused(order):
    db = DB()
    e = engine(db)
    e.kill_switch.set_state(KillSwitchState.PAUSED, "test", "pause")
    assert e.validate_order(order)[0] == RiskDecision.REJECT


def test_daily_loss_exceeded(order):
    assert engine(DB(daily_pnl=-101)).validate_order(order) == (
        RiskDecision.REJECT,
        "daily_loss_exceeded",
    )


def test_position_size_too_large(order):
    order.quantity = 1
    assert engine(DB()).validate_order(order)[1] == "position_size_too_large"


def test_spread_too_wide(order):
    assert engine(DB(spread_bps=10)).validate_order(order)[1] == "spread_too_wide"


def test_stale_data(order):
    assert engine(DB(stale_data=True)).validate_order(order)[1] == "stale_data"


def test_all_checks_pass(order):
    assert engine(DB()).validate_order(order) == (RiskDecision.ALLOW, "ok")


def test_reduce_scenario(order):
    order.quantity = 0.031
    assert engine(DB()).validate_order(order) == (RiskDecision.REDUCE, "position_size_reduce")
