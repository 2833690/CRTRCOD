from packages.backtesting.vectorbt_runner import VectorbtRunner


class ParameterSweep:
    def run(self, df, strategy_cls, param_grid):
        res = VectorbtRunner().parameter_sweep(df, param_grid, lambda d, p: d)
        return (
            res.filter(
                (res["sharpe_ratio"] > 0.5)
                & (res["profit_factor"] > 1.1)
                & (res["num_trades"] >= 30)
            )
            if len(res)
            else res
        )

    def save_candidates(self, candidates, strategy_id):
        return None
