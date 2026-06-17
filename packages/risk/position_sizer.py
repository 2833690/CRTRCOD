class PositionSizer:
    def fixed_fractional(self, capital: float, risk_pct: float, stop_loss_pct: float) -> float:
        return capital * risk_pct / stop_loss_pct

    def fixed_usdt(self, amount: float, max_pct: float, capital: float) -> float:
        return min(amount, capital * max_pct)

    def validate_minimum(self, size_usdt: float, price: float, min_notional: float = 10.0) -> bool:
        return size_usdt >= min_notional and price > 0
