class SlippageModel:
    def estimate(
        self, order_value_usdt: float, candle_volume_usdt: float, base_slippage_pct: float = 0.0005
    ) -> float:
        multiplier = (
            2.0 if candle_volume_usdt and order_value_usdt / candle_volume_usdt > 0.01 else 1.0
        )
        return order_value_usdt * base_slippage_pct * multiplier
