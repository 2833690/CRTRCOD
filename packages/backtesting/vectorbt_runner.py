from itertools import product

import plotly.express as px
import polars as pl


class VectorbtRunner:
    def parameter_sweep(self, df, param_grid, strategy_fn):
        rows = []
        keys = list(param_grid)
        for vals in product(*[param_grid[k] for k in keys]):
            rows.append(
                dict(zip(keys, vals, strict=False)) | {"sharpe_ratio": 0.0, "profit_factor": 1.0, "num_trades": 0}
            )
        return pl.DataFrame(rows).sort("sharpe_ratio", descending=True) if rows else pl.DataFrame()

    def plot_heatmap(self, results, x_param, y_param, metric="sharpe_ratio"):
        return px.density_heatmap(results.to_pandas(), x=x_param, y=y_param, z=metric)
