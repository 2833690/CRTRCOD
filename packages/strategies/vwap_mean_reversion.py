import polars as pl

from packages.features.indicators import IndicatorEngine
from packages.features.liquidity_metrics import LiquidityMetrics

from .base_strategy import BaseStrategy
from .registry import register_strategy


@register_strategy
class VWAPMeanReversion(BaseStrategy):
    strategy_id = "vwap_mean_reversion_v1"
    version = "1.0.0"
    timeframe = "5m"
    min_candles = 60
    vwap_dev_threshold_pct = 0.8
    rsi_oversold = 35
    rsi_overbought = 65
    atr_period = 14
    max_atr_multiplier = 1.5
    volume_min_percentile = 50.0
    max_spread_bps = 5.0
    take_profit_pct = 0.6
    stop_loss_pct = 0.5
    safety_buffer_pct = 0.1

    def populate_indicators(self, df: pl.DataFrame) -> pl.DataFrame:
        e = IndicatorEngine()
        liquidity = LiquidityMetrics()
        df = e.add_ema(df, 21)
        df = e.add_vwap(df)
        df = e.add_rsi(df, 14)
        df = e.add_atr(df, 14)
        df = e.add_vwap_deviation(df)
        df = liquidity.add_volume_percentile(df)
        return liquidity.add_spread_bps(df, "bid", "ask")

    def populate_entry_signal(self, df: pl.DataFrame) -> pl.DataFrame:
        body = (pl.col("close") - pl.col("open")).abs()
        long = (
            (pl.col("vwap_dev_pct") < -self.vwap_dev_threshold_pct)
            & (pl.col("rsi_14") < self.rsi_oversold)
            & (body < pl.col("atr_14") * self.max_atr_multiplier)
            & (pl.col("volume_pct_rank") > self.volume_min_percentile)
        )
        short = (
            (pl.col("vwap_dev_pct") > self.vwap_dev_threshold_pct)
            & (pl.col("rsi_14") > self.rsi_overbought)
            & (body < pl.col("atr_14") * self.max_atr_multiplier)
        )
        return df.with_columns(
            [long.fill_null(False).alias("entry_long"), short.fill_null(False).alias("entry_short")]
        )

    def populate_exit_signal(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            [
                (pl.col("close") >= pl.col("vwap")).fill_null(False).alias("exit_long"),
                (pl.col("close") <= pl.col("vwap")).fill_null(False).alias("exit_short"),
            ]
        )

    def confirm_entry(self, row: dict, market_state: dict) -> bool:
        return (
            row.get("spread_bps", 0) <= self.max_spread_bps
            and market_state.get("expected_profit_pct", 1)
            > market_state.get("fees_slippage_pct", 0) + self.safety_buffer_pct
        )
