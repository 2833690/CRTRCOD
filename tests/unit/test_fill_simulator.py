import pytest
from packages.common.types import OrderSide
from packages.execution.fill_simulator import FillSimulator


def test_simulated_fill():
    assert FillSimulator().simulate_fill(100, OrderSide.BUY, 10, 0.001)[
        "simulated_fill_price"
    ] == pytest.approx(100.15)


def test_fill_quality():
    assert FillSimulator().compare_to_expected(100, 100.1)["deviation_bps"] == pytest.approx(10)


def test_tolerance():
    assert FillSimulator().compare_to_expected(100, 100.1)["within_tolerance"] is True
