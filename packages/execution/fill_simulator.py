from packages.common.types import OrderSide


class FillSimulator:
    def simulate_fill(
        self, signal_price: float, side: OrderSide, spread_bps: float, slippage_pct: float
    ) -> dict:
        direction = 1 if side == OrderSide.BUY else -1
        fill = signal_price * (1 + direction * ((spread_bps / 2) / 10000 + slippage_pct))
        fee = fill * 0.001
        return {
            "simulated_fill_price": fill,
            "fill_quality_bps": abs(fill - signal_price) / signal_price * 10000,
            "fee": fee,
            "effective_cost": fill + fee if side == OrderSide.BUY else fill - fee,
        }

    def compare_to_expected(self, expected_fill: float, actual_fill: float) -> dict:
        deviation = abs(actual_fill - expected_fill) / expected_fill * 10000
        return {"deviation_bps": deviation, "within_tolerance": deviation <= 20.0}
