import polars as pl


class LiquidityMetrics:
    def add_spread_bps(
        self, df: pl.DataFrame, bid_col: str = "bid", ask_col: str = "ask"
    ) -> pl.DataFrame:
        if bid_col not in df.columns or ask_col not in df.columns:
            return df.with_columns(pl.lit(0.0).alias("spread_bps"))
        return df.with_columns(
            (
                (pl.col(ask_col) - pl.col(bid_col))
                / ((pl.col(ask_col) + pl.col(bid_col)) / 2)
                * 10000
            ).alias("spread_bps")
        )

    def add_volume_percentile(self, df: pl.DataFrame, period: int = 20) -> pl.DataFrame:
        return df.with_columns(
            (pl.col("volume").rank() / pl.len() * 100).shift(1).alias("volume_pct_rank")
        )

    def add_liquidity_score(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            (pl.col("volume_pct_rank").fill_null(50) - pl.col("spread_bps").fill_null(0))
            .clip(0, 100)
            .alias("liquidity_score")
        )
