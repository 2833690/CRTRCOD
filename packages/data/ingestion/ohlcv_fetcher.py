from datetime import UTC, datetime, timedelta

import polars as pl

from .gap_detector import GapDetector


class OHLCVFetcher:
    def __init__(self, client, storage):
        self.client = client
        self.storage = storage
        self.gap_detector = GapDetector()

    def fetch_and_store(self, exchange, symbol, timeframe, since, until):
        rows = []
        cur = int(since.timestamp() * 1000)
        while datetime.fromtimestamp(cur / 1000, UTC) < until:
            batch = self.client.fetch_ohlcv(symbol, timeframe, cur, 1000) or []
            if not batch:
                break
            rows.extend(batch)
            cur = batch[-1][0] + 1
        df = (
            pl.DataFrame(
                rows,
                schema=["timestamp_ms", "open", "high", "low", "close", "volume"],
                orient="row",
            )
            .with_columns(
                [
                    pl.from_epoch("timestamp_ms", time_unit="ms")
                    .dt.replace_time_zone("UTC")
                    .alias("timestamp_utc"),
                    pl.lit("ccxt").alias("source"),
                    pl.lit(symbol).alias("symbol"),
                    pl.lit(timeframe).alias("timeframe"),
                    pl.lit(exchange).alias("exchange"),
                    pl.lit(datetime.now(UTC)).alias("ingest_ts"),
                ]
            )
            .drop("timestamp_ms")
            if rows
            else pl.DataFrame()
        )
        if len(df):
            self.storage.write(
                df, self.storage.build_path(exchange, symbol, timeframe, since.date())
            )
        return df

    def backfill(self, exchange, symbols, timeframes, days):
        until = datetime.now(UTC)
        since = until - timedelta(days=days)
        for s in symbols:
            for tf in timeframes:
                self.fetch_and_store(exchange, s, tf, since, until)
