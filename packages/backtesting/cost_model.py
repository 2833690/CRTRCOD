from dataclasses import dataclass


@dataclass
class FeeSchedule:
    maker_fee_pct: float = 0.001
    taker_fee_pct: float = 0.001
    use_bnb_discount: bool = False


@dataclass
class SlippageModel:
    base_slippage_pct: float = 0.0005
    volume_adjustment: bool = True
    volume_threshold_pct: float = 0.01
    extra_slippage_multiplier: float = 2.0


class CostModel:
    def __init__(self, fees: FeeSchedule | None = None, slippage: SlippageModel | None = None):
        self.fees = fees or FeeSchedule()
        self.slippage = slippage or SlippageModel()

    def _fee_rate(self, order_type):
        r = self.fees.maker_fee_pct if order_type == "limit" else self.fees.taker_fee_pct
        return r * 0.75 if self.fees.use_bnb_discount else r

    def _slip(self, price, quantity, candle_volume):
        pct = self.slippage.base_slippage_pct
        if (
            self.slippage.volume_adjustment
            and candle_volume
            and quantity / candle_volume > self.slippage.volume_threshold_pct
        ):
            pct *= self.slippage.extra_slippage_multiplier
        return price * quantity * pct

    def calculate_entry_cost(self, price, quantity, order_type, candle_volume):
        notional = price * quantity
        fee = notional * self._fee_rate(order_type)
        slip = self._slip(price, quantity, candle_volume)
        return {
            "fee": fee,
            "slippage": slip,
            "total_cost": fee + slip,
            "effective_price": price + (slip / quantity if quantity else 0),
        }

    def calculate_exit_cost(self, price, quantity, order_type, candle_volume):
        d = self.calculate_entry_cost(price, quantity, order_type, candle_volume)
        d["effective_price"] = price - (d["slippage"] / quantity if quantity else 0)
        return d

    def apply_to_trade(self, entry, exit_, quantity):
        gross = (exit_["price"] - entry["price"]) * quantity
        ec = self.calculate_entry_cost(
            entry["price"],
            quantity,
            entry.get("order_type", "market"),
            entry.get("candle_volume", 0),
        )
        xc = self.calculate_exit_cost(
            exit_["price"],
            quantity,
            exit_.get("order_type", "market"),
            exit_.get("candle_volume", 0),
        )
        fees = ec["fee"] + xc["fee"]
        slips = ec["slippage"] + xc["slippage"]
        return {
            "gross_pnl": gross,
            "fees_total": fees,
            "slippage_total": slips,
            "net_pnl": gross - fees - slips,
        }
