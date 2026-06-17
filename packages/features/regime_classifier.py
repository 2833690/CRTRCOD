from enum import Enum

import polars as pl


class MarketRegime(str, Enum):
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    HIGH_VOL_RANGE = "high_vol_range"
    LOW_VOL_RANGE = "low_vol_range"
    UNKNOWN = "unknown"


class RegimeClassifier:
    def classify(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns(
            pl.col("atr_14").rolling_mean(30 * 24 * 12).alias("atr_30d_avg")
            if "atr_14" in df.columns
            else pl.lit(None).alias("atr_30d_avg")
        )
        return df.with_columns(
            pl.when((pl.col("adx_14") > 25) & (pl.col("ema_21") > pl.col("ema_55")))
            .then(pl.lit(MarketRegime.BULL_TREND.value))
            .when((pl.col("adx_14") > 25) & (pl.col("ema_21") < pl.col("ema_55")))
            .then(pl.lit(MarketRegime.BEAR_TREND.value))
            .when(pl.col("atr_14") > pl.col("atr_30d_avg") * 1.5)
            .then(pl.lit(MarketRegime.HIGH_VOL_RANGE.value))
            .otherwise(pl.lit(MarketRegime.LOW_VOL_RANGE.value))
            .alias("regime")
        )
