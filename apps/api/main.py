import time

from fastapi import FastAPI, Request
from packages.common.config import get_settings
from packages.common.logging import get_logger
from slowapi import Limiter
from slowapi.util import get_remote_address

from apps.api.routers import backtests, data, paper, risk, strategies

logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CRTRCOD API", version="0.1.0")
app.state.limiter = limiter


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": (time.perf_counter() - start) * 1000,
        },
    )
    return response


@app.on_event("startup")
async def startup():
    get_settings()
    logger.info("crtrcod_api_started")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(risk.router, prefix="/v1/risk", tags=["risk"])
app.include_router(strategies.router, prefix="/v1/strategies", tags=["strategies"])

app.include_router(data.router, prefix="/v1/data", tags=["data"])
app.include_router(backtests.router, prefix="/v1/backtests", tags=["backtests"])
app.include_router(paper.router, prefix="/v1/paper", tags=["paper"])
