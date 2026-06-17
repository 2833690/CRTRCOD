from datetime import UTC, datetime
from types import SimpleNamespace

from packages.common.types import KillSwitchState, OrderSide, RiskDecision
from packages.risk.engine import OrderRequest, RiskEngine
from packages.risk.kill_switch import KillSwitch
from packages.risk.limits import RiskLimits


def order():
    return OrderRequest(
        "s", "BTC/USDT", OrderSide.BUY, "limit", 0.01, 10000, "5m", datetime.now(UTC)
    )


def test_daily_loss_blocks():
    db = SimpleNamespace(
        audit_log=[],
        total_capital=10000,
        daily_pnl=-999,
        open_positions=0,
        spread_bps=0,
        stale_data=False,
    )
    assert (
        RiskEngine(RiskLimits(), KillSwitch(db_session=db), db).validate_order(order())[0]
        == RiskDecision.REJECT
    )


def test_emergency_blocks():
    db = SimpleNamespace(
        audit_log=[],
        total_capital=10000,
        daily_pnl=0,
        open_positions=0,
        spread_bps=0,
        stale_data=False,
    )
    ks = KillSwitch(db_session=db)
    ks.set_state(KillSwitchState.EMERGENCY, "x", "y")
    assert RiskEngine(RiskLimits(), ks, db).validate_order(order())[1] == "kill_switch_active"


def test_audit_per_call():
    db = SimpleNamespace(
        audit_log=[],
        total_capital=10000,
        daily_pnl=0,
        open_positions=0,
        spread_bps=0,
        stale_data=False,
    )
    e = RiskEngine(RiskLimits(), KillSwitch(db_session=db), db)
    e.validate_order(order())
    e.validate_order(order())
    assert len(db.audit_log) == 2
