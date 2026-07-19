from src.analytics.cashflow_kpis import *


def test_free_cash_flow():
    assert free_cash_flow(500, -200) == 300


def test_negative_fcf():
    assert free_cash_flow(100, -300) == -200


def test_cfo_quality():
    assert cfo_quality_score(
        [100,120],
        [80,100]
    ) == "High Quality"


def test_pat_zero():
    assert cfo_quality_score(
        [100],
        [0]
    ) is None


def test_capex():
    value, label = capex_intensity(-50,1000)

    assert value == 5.0
    assert label == "Moderate"


def test_fcf_conversion():
    assert fcf_conversion_rate(300,500) == 60.0


def test_operating_profit_zero():
    assert fcf_conversion_rate(100,0) is None


def test_pattern():
    assert capital_allocation_pattern(
        100,-50,-30,1.2
    ) == "Shareholder Returns"

from src.analytics.cashflow_kpis import generate_capital_allocation

