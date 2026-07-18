import pytest

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    check_opm_difference,
    roe,
    roce,
    roa,
    financial_sector_roce_check,
)


# --------------------------------------------------
# Net Profit Margin
# --------------------------------------------------

def test_net_profit_margin():
    assert net_profit_margin(200, 1000) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


# --------------------------------------------------
# Operating Profit Margin
# --------------------------------------------------

def test_operating_profit_margin():
    assert operating_profit_margin(150, 1000) == 15.0


def test_opm_difference():
    assert check_opm_difference(20, 18) is True


# --------------------------------------------------
# ROE
# --------------------------------------------------

def test_roe():
    assert roe(200, 500, 500) == 20.0


def test_roe_negative_equity():
    assert roe(100, -500, 200) is None


# --------------------------------------------------
# ROCE
# --------------------------------------------------

def test_roce():
    assert round(roce(300, 500, 500, 500), 2) == 20.0


# --------------------------------------------------
# ROA
# --------------------------------------------------

def test_roa():
    assert roa(200, 4000) == 5.0