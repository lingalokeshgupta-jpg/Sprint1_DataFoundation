import pytest

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover,
)


def test_debt_free_returns_zero():
    assert debt_to_equity(0, 500, 500) == 0


def test_debt_to_equity():
    assert debt_to_equity(1000, 500, 500) == 1.0


def test_negative_equity():
    assert debt_to_equity(500, -500, 200) is None


def test_high_leverage_flag():
    assert high_leverage_flag(6, "Industrials") is True


def test_financial_sector_no_flag():
    assert high_leverage_flag(6, "Financials") is False


def test_interest_zero():
    assert interest_coverage_ratio(100, 20, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_asset_turnover():
    assert asset_turnover(1000, 5000) == 0.2