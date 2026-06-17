import time

from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from apps.api.routers import risk, strategies
from packages.common.config import get_settings
from packages.common.logging import get_logger

logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CRTRCOD API")
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
