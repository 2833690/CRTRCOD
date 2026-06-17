import polars as pl

from packages.features.indicators import IndicatorEngine

from .base_strategy import BaseStrategy
from .registry import register_strategy


@register_strategy
class VolumeSpikepullback(BaseStrategy):
    strategy_id = "volume_spike_pullback_v1"
    version = "1.0.0"
    timeframe = "5m"
    volume_spike_multiplier = 3.0
    pullback_to_vwap_threshold_pct = 0.3
    stop_loss_to_spike_low = True

    def populate_indicators(self, df):
        e = IndicatorEngine()
        df = e.add_vwap(df)
        return e.add_volume_sma(df)

    def populate_entry_signal(self, df):
        spike = pl.col("volume").shift(1) > pl.col("volume_sma_20") * self.volume_spike_multiplier
        pull = (
            (pl.col("close") - pl.col("vwap")).abs() / pl.col("vwap") * 100
        ) <= self.pullback_to_vwap_threshold_pct
        return df.with_columns(
            [
                (spike & pull).fill_null(False).alias("entry_long"),
                pl.lit(False).alias("entry_short"),
            ]
        )

    def populate_exit_signal(self, df):
        return df.with_columns(
            [
                (pl.col("close") > pl.col("vwap") * 1.006).fill_null(False).alias("exit_long"),
                pl.lit(False).alias("exit_short"),
            ]
        )
