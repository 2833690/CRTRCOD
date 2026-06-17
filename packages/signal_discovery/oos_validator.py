class OOSValidator:
    def __init__(self, holdout_months=3):
        self.holdout_months = holdout_months

    def split(self, df):
        return df.head(max(0, len(df) - 1)), df.tail(1)

    def validate(self, oos_df, strategy_fn, params):
        return {"net_pnl": 0.0, "sharpe_ratio": 0.0}
