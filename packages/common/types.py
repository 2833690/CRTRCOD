from dataclasses import dataclass
from datetime import datetime
from enum import Enum, StrEnum
from typing import TypedDict


class Exchange(StrEnum):
    BINANCE = "binance"
    KRAKEN = "kraken"
    OKX = "okx"


class Timeframe(StrEnum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class StrategyStatus(StrEnum):
    RESEARCH = "research"
    VALIDATED = "validated"
    PAPER = "paper"
    LIVE = "live"
    DISABLED = "disabled"


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class RiskDecision(StrEnum):
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

@dataclass(frozen=True)
class Trade:
    entry_ts: datetime
    exit_ts: datetime
    symbol: str
    side: OrderSide
    quantity: float
    entry_price: float
    exit_price: float
    gross_pnl: float
    fees: float
    slippage: float
    net_pnl: float
