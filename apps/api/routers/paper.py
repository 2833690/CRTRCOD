from fastapi import APIRouter

router = APIRouter()
@router.get("")
def paper_status() -> dict[str, object]:
    return {"status": "idle", "mode": "paper", "live_trading_enabled": False}
