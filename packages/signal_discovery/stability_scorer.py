class StabilityScorer:
    def score(
        self, walk_forward_result, oos_metrics, param_robustness, regime_breadth, stress_score
    ):
        return max(
            0.0,
            min(
                100.0,
                walk_forward_result.get("consistency_pct", 0) * 0.3
                + oos_metrics.get("sharpe_ratio", 0) * 10
                + param_robustness * 20
                + regime_breadth * 20
                + stress_score * 20,
            ),
        )
