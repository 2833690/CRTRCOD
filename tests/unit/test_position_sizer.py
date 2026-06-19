from packages.risk.position_sizer import PositionSizer


def test_fixed_fractional():
    assert PositionSizer().fixed_fractional(10000, 0.01, 0.05) == 2000

def test_capped_fixed_usdt():
    assert PositionSizer().fixed_usdt(1000, 0.03, 10000) == 300

def test_minimum_notional():
    s = PositionSizer()
    assert s.validate_minimum(10, 100)
    assert not s.validate_minimum(9.99, 100)
