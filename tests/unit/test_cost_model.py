import pytest
from packages.backtesting.cost_model import CostModel


def test_fee_calculation():
    assert CostModel().calculate_entry_cost(100, 1, "market", 1000)["fee"] == pytest.approx(0.1)


def test_slippage_calculation():
    assert CostModel().calculate_entry_cost(100, 1, "market", 1000)["slippage"] == pytest.approx(
        0.05
    )


def test_net_pnl():
    assert CostModel().apply_to_trade(
        {"price": 100, "candle_volume": 1000}, {"price": 110, "candle_volume": 1000}, 1
    )["net_pnl"] == pytest.approx(10 - 0.21 - 0.105)


def test_volume_adjusted_slippage():
    assert CostModel().calculate_entry_cost(100, 20, "market", 1000)["slippage"] == pytest.approx(
        2.0
    )
