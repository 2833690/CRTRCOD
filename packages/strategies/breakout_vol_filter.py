import polars as pl

from packages.features.indicators import IndicatorEngine

from .base_strategy import BaseStrategy
from .registry import register_strategy


@register_strategy
class BreakoutVolFilter(BaseStrategy):
    strategy_id = "breakout_vol_filter_v1"
    version = "1.0.0"
    timeframe = "15m"
    bb_period = 20
    bb_std = 2.0
    volume_spike_multiplier = 1.5
    rsi_min = 45
    rsi_max = 65
    adx_min = 20

    def populate_indicators(self, df):
        e = IndicatorEngine()
        df = e.add_bollinger(df, self.bb_period, self.bb_std)
        df = e.add_rsi(df)
        df = e.add_adx(df)
        return e.add_volume_sma(df)

    def populate_entry_signal(self, df):
        squeeze = pl.col("bb_width") < pl.col("bb_width").rolling_quantile(0.2, window_size=50)
        vol = pl.col("volume") > pl.col("volume_sma_20") * self.volume_spike_multiplier
        long = (
            squeeze
            & (pl.col("close") > pl.col("bb_upper"))
            & vol
            & (pl.col("rsi_14").is_between(self.rsi_min, self.rsi_max))
            & (pl.col("adx_14") > self.adx_min)
        )
        return df.with_columns(
            [long.fill_null(False).alias("entry_long"), pl.lit(False).alias("entry_short")]
        )

    def populate_exit_signal(self, df):
        return df.with_columns(
            [
                (pl.col("close") < pl.col("bb_mid")).fill_null(False).alias("exit_long"),
                pl.lit(False).alias("exit_short"),
            ]
        )
