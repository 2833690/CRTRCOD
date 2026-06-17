from datetime import timedelta

INTERVAL = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}


class GapDetector:
    def find_gaps(self, df, timeframe):
        rows = df.sort("timestamp_utc")["timestamp_utc"].to_list()
        exp = timedelta(seconds=INTERVAL[timeframe])
        gaps = []
        for a, b in zip(rows, rows[1:], strict=False):
            if b - a > exp * 1.5:
                gaps.append({"start": a, "end": b, "duration_candles": int((b - a) / exp) - 1})
        return gaps

    def log_gaps(self, gaps, symbol, exchange):
        return None
