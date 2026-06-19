import time

import ccxt


class CCXTClient:
    def __init__(self, exchange_name: str, api_key: str = "", secret: str = ""):
        cls = getattr(ccxt, exchange_name)
        self.exchange = cls({"apiKey": api_key, "secret": secret, "enableRateLimit": True})

    def verify_permissions(self) -> dict:
        perms: dict[str, object] = getattr(self.exchange, "fetch_permissions", lambda: {})()
        if perms.get("withdraw") or perms.get("withdrawal"):
            raise PermissionError("Withdrawal permission must be disabled")
        return perms

    def fetch_ohlcv(self, symbol, timeframe, since_ms, limit):
        for i in range(5):
            try:
                return self.exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)
            except Exception:
                if i == 4:
                    raise
                time.sleep(2**i / 10)

    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)

    def fetch_order_book(self, symbol, limit=20):
        return self.exchange.fetch_order_book(symbol, limit=limit)
