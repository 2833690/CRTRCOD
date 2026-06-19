from fastapi import APIRouter
from packages.common.types import Exchange, Timeframe

router = APIRouter()
@router.get("")
def supported_data() -> dict[str, list[str]]:
    return {"exchanges": [e.value for e in Exchange], "timeframes": [t.value for t in Timeframe]}
