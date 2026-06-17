from pathlib import Path


class ReportGenerator:
    def generate_html(self, metrics: dict, trades, equity_curve) -> str:
        return "<html><body><h1>CRTRCOD Backtest</h1></body></html>"

    def generate_markdown(self, metrics: dict) -> str:
        rows = ["| Metric | Value |", "|---|---|"]
        rows.extend(f"| {key} | {value} |" for key, value in metrics.items())
        return "\n".join(rows)

    def save_to_file(self, content: str, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content)
