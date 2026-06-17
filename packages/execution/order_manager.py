from uuid import uuid4


class OrderManager:
    def __init__(self):
        self.positions = {}
        self.closed = []

    def open_position(
        self, symbol, side, quantity, entry_price, stop_loss, take_profit, strategy_id
    ) -> str:
        pid = str(uuid4())
        self.positions[pid] = locals() | {"position_id": pid}
        return pid

    def close_position(self, position_id, exit_price, reason):
        p = self.positions.pop(position_id)
        p["exit_price"] = exit_price
        p["reason"] = reason
        p["pnl"] = (exit_price - p["entry_price"]) * p["quantity"]
        self.closed.append(p)
        return p

    def get_open_positions(self):
        return list(self.positions.values())

    def get_daily_pnl(self):
        return sum(p.get("pnl", 0) for p in self.closed)
