from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class KillSwitchBody(BaseModel):
    state: int
    reason: str


@router.get("/status")
def status():
    return {"kill_switch_state": 0, "daily_pnl": 0.0, "daily_loss_limit": 0.01, "open_positions": 0}


@router.post("/kill-switch")
def set_kill_switch(body: KillSwitchBody):
    return {"state": body.state, "reason": body.reason}


@router.get("/circuit-breakers")
def circuit_breakers():
    return {"consecutive_losses": False, "slippage_anomaly": False, "data_feed_stale": False}


@router.get("/audit-log")
def audit_log():
    return []
