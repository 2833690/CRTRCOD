from fastapi import APIRouter

router = APIRouter()
@router.get("")
def demo_backtest() -> dict[str, object]:
    return {"status": "placeholder", "live_trading": "disabled", "message": "Run scripts/run_backtest_demo.py for a local demo."}
