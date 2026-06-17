from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TypedDict


class Exchange(str, Enum):
    BINANCE = "binance"
    KRAKEN = "kraken"
    OKX = "okx"


class Timeframe(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class StrategyStatus(str, Enum):
    RESEARCH = "research"
    VALIDATED = "validated"
    PAPER = "paper"
    LIVE = "live"
    DISABLED = "disabled"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class RiskDecision(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    REDUCE = "REDUCE"


class KillSwitchState(int, Enum):
    ACTIVE = 0
    PAUSED = 1
    CLOSED = 2
    EMERGENCY = 3


@dataclass
class Symbol:
    base: str
    quote: str

    def __str__(self) -> str:
        return f"{self.base}/{self.quote}"

    @classmethod
    def from_string(cls, s: str) -> "Symbol":
        base, quote = s.split("/")
        return cls(base, quote)


@dataclass
class OHLCVRecord:
    timestamp_utc: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    symbol: str
    timeframe: str
    exchange: str
    ingest_ts: datetime


class OHLCVDict(TypedDict):
    timestamp_utc: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    symbol: str
    timeframe: str
    exchange: str
    ingest_ts: datetime
