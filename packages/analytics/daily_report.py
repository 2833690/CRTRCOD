class DailyReportGenerator:
    def generate(self, date):
        return {"date": str(date), "daily_pnl": 0.0, "trades": 0}

    def render_markdown(self, report):
        return f"# Daily Report\nPnL: {report.get('daily_pnl', 0)}"

    def send_via_telegram(self, report, alert_service):
        alert_service.send_daily_report(report)
