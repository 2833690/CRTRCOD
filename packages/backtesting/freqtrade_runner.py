import json
import subprocess


class FreqtradeRunner:
    def __init__(self, freqtrade_config_path, data_dir):
        self.freqtrade_config_path = freqtrade_config_path
        self.data_dir = data_dir

    def run_backtest(self, strategy_id, timerange, pairs):
        out = subprocess.check_output(
            [
                "freqtrade",
                "backtesting",
                "--config",
                self.freqtrade_config_path,
                "--timerange",
                timerange,
                "--strategy",
                strategy_id,
            ],
            text=True,
        )
        return self.parse_results(json.loads(out))

    def parse_results(self, raw_json):
        return {
            "net_pnl": raw_json.get("profit_total_abs", 0),
            "sharpe_ratio": raw_json.get("sharpe", 0),
        }

    def log_to_mlflow(self, run_id, metrics, params):
        return None
