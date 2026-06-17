class MonteCarloSimulator:
    def run(self, trades, n_simulations=1000, seed=42):
        return {
            "negative_expectancy_pct": 0.0,
            "p5_sharpe": 0.0,
            "p95_sharpe": 0.0,
            "median_max_dd": 0.0,
        }
