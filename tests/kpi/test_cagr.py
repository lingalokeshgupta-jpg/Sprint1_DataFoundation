import pytest

from src.analytics.cagr import (
    calculate_cagr,
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)


def test_normal_cagr():

    value, flag = calculate_cagr(100, 200, 5)

    assert round(value, 2) == 14.87
    assert flag is None


def test_decline_to_loss():

    value, flag = calculate_cagr(100, -50, 5)

    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_turnaround():

    value, flag = calculate_cagr(-100, 200, 5)

    assert value is None
    assert flag == "TURNAROUND"


def test_both_negative():

    value, flag = calculate_cagr(-100, -50, 5)

    assert value is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():

    value, flag = calculate_cagr(0, 200, 5)

    assert value is None
    assert flag == "ZERO_BASE"


def test_insufficient():

    value, flag = calculate_cagr(None, 200, 5)

    assert value is None
    assert flag == "INSUFFICIENT"


def test_revenue_cagr():

    value, _ = revenue_cagr(100, 200, 5)

    assert round(value, 2) == 14.87


def test_pat_cagr():

    value, _ = pat_cagr(50, 100, 5)

    assert round(value, 2) == 14.87


def test_eps_cagr():

    value, _ = eps_cagr(10, 20, 5)

    assert round(value, 2) == 14.87


def test_invalid_years():

    value, flag = calculate_cagr(100, 200, 0)

    assert value is None
    assert flag == "INSUFFICIENT"