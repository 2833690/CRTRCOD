from abc import ABC, abstractmethod

import polars as pl


class BaseStrategy(ABC):
    strategy_id: str
    version: str = "1.0.0"
    timeframe: str
    min_candles: int = 50

    @abstractmethod
    def populate_indicators(self, df: pl.DataFrame) -> pl.DataFrame: ...
    @abstractmethod
    def populate_entry_signal(self, df: pl.DataFrame) -> pl.DataFrame: ...
    @abstractmethod
    def populate_exit_signal(self, df: pl.DataFrame) -> pl.DataFrame: ...
    def confirm_entry(self, row: dict, market_state: dict) -> bool:
        return True

    def get_stop_loss(self, entry_price: float, atr: float) -> float:
        return entry_price - atr

    def get_take_profit(self, entry_price: float, atr: float) -> float:
        return entry_price + (atr * 1.5)

    def should_disable(self, stats: dict) -> tuple[bool, str]:
        return False, ""
