from celery import Celery
from celery.schedules import crontab
from packages.common.config import get_settings

settings = get_settings()
celery_app = Celery("crtrcod", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "data.ingest_ohlcv": {"task": "data.ingest_ohlcv", "schedule": 300},
    "paper_trading.tick": {"task": "paper_trading.tick", "schedule": 60},
    "analytics.daily_report": {
        "task": "analytics.daily_report",
        "schedule": crontab(hour=23, minute=59),
    },
}


@celery_app.task(name="data.ingest_ohlcv")
def ingest_ohlcv():
    return "ok"


@celery_app.task(name="paper_trading.tick")
def paper_tick():
    return "ok"


@celery_app.task(name="analytics.daily_report")
def daily_report():
    return "ok"
