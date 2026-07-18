"""
Sprint 2
Day 10
CAGR Engine
"""

from math import pow


# --------------------------------------------------
# Generic CAGR Engine
# --------------------------------------------------

def calculate_cagr(start_value, end_value, years):
    """
    Returns:
        (cagr_value, flag)

    Flag:
        None
        DECLINE_TO_LOSS
        TURNAROUND
        BOTH_NEGATIVE
        ZERO_BASE
        INSUFFICIENT
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value is None or end_value is None:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    cagr = (
        (pow(end_value / start_value, 1 / years) - 1)
        * 100
    )

    return round(cagr, 2), None


# --------------------------------------------------
# Revenue CAGR
# --------------------------------------------------

def revenue_cagr(start_sales, end_sales, years):

    return calculate_cagr(
        start_sales,
        end_sales,
        years
    )


# --------------------------------------------------
# PAT CAGR
# --------------------------------------------------

def pat_cagr(start_pat, end_pat, years):

    return calculate_cagr(
        start_pat,
        end_pat,
        years
    )


# --------------------------------------------------
# EPS CAGR
# --------------------------------------------------

def eps_cagr(start_eps, end_eps, years):

    return calculate_cagr(
        start_eps,
        end_eps,
        years
    )