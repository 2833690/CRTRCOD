from datetime import UTC, datetime

import polars as pl
from pydantic import BaseModel, field_validator, model_validator


class OHLCVSchema(BaseModel):
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

    @field_validator("open", "high", "low", "close", "volume")
    @classmethod
    def positive(cls, v):
        if v <= 0:
            raise ValueError("must be > 0")
        return v

    @field_validator("timestamp_utc")
    @classmethod
    def utc(cls, v):
        if v.tzinfo is None or v.utcoffset() != UTC.utcoffset(v):
            raise ValueError("timestamp_utc must be UTC")
        return v

    @model_validator(mode="after")
    def ohlc(self):
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("invalid OHLC")
        return self


def validate_dataframe(df: pl.DataFrame):
    good = []
    bad = []
    for row in df.to_dicts():
        try:
            good.append(OHLCVSchema(**row).model_dump())
        except Exception as e:
            bad.append({"row": row, "error": str(e)})
    return pl.DataFrame(good) if good else pl.DataFrame(), bad
