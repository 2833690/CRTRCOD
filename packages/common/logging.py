import json
import logging
from datetime import UTC, datetime

SENSITIVE = {"api_key", "secret", "password", "token"}


def _clean(v):
    if isinstance(v, dict):
        return {
            k: ("***" if any(s in k.lower() for s in SENSITIVE) else _clean(val))
            for k, val in v.items()
        }
    return v


class JsonFormatter(logging.Formatter):
    def format(self, record):
        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord("", 0, "", 0, "", (), None).__dict__
        }
        return json.dumps(
            {
                "ts": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
                "extra": _clean(extra),
            },
            default=str,
        )


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(JsonFormatter())
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
