class FillQualityAnalyzer:
    def analyze(self, strategy_id, days=14):
        return {
            "avg_fill_deviation_bps": 0,
            "max_fill_deviation_bps": 0,
            "within_tolerance_pct": 100,
            "slippage_vs_expected_ratio": 1,
        }

    def is_within_tolerance(self, avg_deviation_bps, tolerance_bps=20.0):
        return avg_deviation_bps <= tolerance_bps
