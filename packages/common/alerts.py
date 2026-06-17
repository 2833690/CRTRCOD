import re

import httpx

from .config import get_settings
from .logging import get_logger

logger = get_logger(__name__)


class AlertService:
    def __init__(self):
        self.settings = get_settings()

    def _sanitize(self, msg: str) -> str:
        return re.sub(r"(?i)(api[_-]?key|secret|password|token)=\S+", r"=***", msg)

    def send_telegram(self, message: str) -> None:
        if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
            logger.warning("telegram_not_configured")
            return
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        httpx.post(
            url,
            json={"chat_id": self.settings.telegram_chat_id, "text": self._sanitize(message)},
            timeout=10,
        ).raise_for_status()

    def send_daily_report(self, report: dict) -> None:
        self.send_telegram(
            f"Daily PnL: {report.get('daily_pnl', 0)} | Trades: {report.get('trades', 0)}"
        )
