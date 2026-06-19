from fastapi import APIRouter
from packages.strategies.registry import StrategyRegistry

router = APIRouter()


@router.get("")
def list_strategies():
    return [{"strategy_id": s, "status": "research"} for s in StrategyRegistry.list_all()]


@router.get("/{strategy_id}")
def detail(strategy_id: str):
    return {"strategy_id": strategy_id, "metrics": {}}


@router.post("/{strategy_id}/approve")
def approve(strategy_id: str):
    return {"strategy_id": strategy_id, "approved": True}


@router.post("/{strategy_id}/enable-live")
def enable_live(strategy_id: str):
    return {"strategy_id": strategy_id, "live_enabled": True}
