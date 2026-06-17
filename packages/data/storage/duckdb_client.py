import duckdb


class DuckDBClient:
    def __init__(self, db_path: str = "data/research.duckdb"):
        self.conn = duckdb.connect(db_path)

    def query(self, sql: str, params: dict | None = None):
        return self.conn.execute(sql, params or {}).pl()

    def execute(self, sql: str, params: dict | None = None) -> None:
        self.conn.execute(sql, params or {})

    def load_parquet_glob(self, pattern: str, table_name: str) -> None:
        self.execute(
            f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{pattern}')"
        )

    def get_ohlcv(self, symbol, timeframe, start, end):
        return self.query(
            "select * from ohlcv where symbol=$symbol and timeframe=$timeframe and timestamp_utc between $start and $end",
            locals(),
        )
