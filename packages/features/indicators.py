import polars as pl


class IndicatorEngine:
    def add_ema(self, df: pl.DataFrame, period: int, column: str = "close") -> pl.DataFrame:
        return df.with_columns(pl.col(column).ewm_mean(span=period).shift(1).alias(f"ema_{period}"))

    def add_vwap(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            ((pl.col("close") * pl.col("volume")).cum_sum() / pl.col("volume").cum_sum())
            .shift(1)
            .alias("vwap")
        )

    def add_rsi(self, df: pl.DataFrame, period: int = 14) -> pl.DataFrame:
        d = pl.col("close").diff()
        up = pl.when(d > 0).then(d).otherwise(0).rolling_mean(period)
        down = pl.when(d < 0).then(-d).otherwise(0).rolling_mean(period)
        return df.with_columns((100 - (100 / (1 + up / down))).shift(1).alias(f"rsi_{period}"))

    def add_atr(self, df: pl.DataFrame, period: int = 14) -> pl.DataFrame:
        tr = pl.max_horizontal(
            (pl.col("high") - pl.col("low")),
            (pl.col("high") - pl.col("close").shift()).abs(),
            (pl.col("low") - pl.col("close").shift()).abs(),
        )
        return df.with_columns(tr.rolling_mean(period).shift(1).alias(f"atr_{period}"))

    def add_bollinger(self, df: pl.DataFrame, period: int = 20, std: float = 2.0) -> pl.DataFrame:
        mid = pl.col("close").rolling_mean(period)
        sd = pl.col("close").rolling_std(period)
        upper = mid + sd * std
        lower = mid - sd * std
        return df.with_columns(
            [
                mid.shift(1).alias("bb_mid"),
                upper.shift(1).alias("bb_upper"),
                lower.shift(1).alias("bb_lower"),
                ((upper - lower) / mid).shift(1).alias("bb_width"),
            ]
        )

    def add_adx(self, df: pl.DataFrame, period: int = 14) -> pl.DataFrame:
        return df.with_columns(
            ((pl.col("high") - pl.col("low")) / pl.col("close") * 100)
            .rolling_mean(period)
            .shift(1)
            .alias(f"adx_{period}")
        )

    def add_volume_sma(self, df: pl.DataFrame, period: int = 20) -> pl.DataFrame:
        return df.with_columns(
            pl.col("volume").rolling_mean(period).shift(1).alias(f"volume_sma_{period}")
        )

    def add_vwap_deviation(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            ((pl.col("close") - pl.col("vwap")) / pl.col("vwap") * 100).alias("vwap_dev_pct")
        )

    def add_all(self, df: pl.DataFrame) -> pl.DataFrame:
        for f in [
            lambda x: self.add_ema(x, 21),
            lambda x: self.add_ema(x, 55),
            self.add_vwap,
            self.add_rsi,
            self.add_atr,
            self.add_bollinger,
            self.add_adx,
            self.add_volume_sma,
            self.add_vwap_deviation,
        ]:
            df = f(df)
        return df
