from pathlib import Path

import polars as pl


class ParquetWriter:
    def write(self, df: pl.DataFrame, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            raise FileExistsError(path)
        df.write_parquet(p)

    def read(self, path: str) -> pl.DataFrame:
        return pl.read_parquet(path)

    def list_files(self, exchange, symbol, timeframe) -> list[str]:
        return sorted(
            str(p) for p in Path(f"data/raw/{exchange}/{symbol}/{timeframe}").glob("*.parquet")
        )

    def build_path(self, exchange, symbol, timeframe, date) -> str:
        return f"data/raw/{exchange}/{symbol.replace('/', '-')}/{timeframe}/{date:%Y-%m-%d}.parquet"
