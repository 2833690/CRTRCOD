class WalkForwardValidator:
    def __init__(self, train_months=6, test_months=2, min_folds=5):
        self.train_months = train_months
        self.test_months = test_months
        self.min_folds = min_folds

    def run(self, df, strategy_fn, params):
        return {"folds": [], "consistency_pct": 0.0, "avg_sharpe": 0.0, "sharpe_variance": 0.0}
