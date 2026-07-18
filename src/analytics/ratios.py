"""
Profitability Ratio Engine
Sprint 2 - Day 08
"""

# --------------------------------------------------
# Net Profit Margin
# --------------------------------------------------

def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = Net Profit / Sales * 100
    """

    if sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)


# --------------------------------------------------
# Operating Profit Margin
# --------------------------------------------------

def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = Operating Profit / Sales *100
    """

    if sales == 0:
        return None

    return round((operating_profit / sales) * 100, 2)


# --------------------------------------------------
# OPM Cross Check
# --------------------------------------------------

def check_opm_difference(calculated_opm, source_opm):
    """
    Returns True if difference >1%
    """

    if calculated_opm is None or source_opm is None:
        return False

    return abs(calculated_opm - source_opm) > 1


# --------------------------------------------------
# Return On Equity
# --------------------------------------------------

def roe(net_profit, equity_capital, reserves):

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


# --------------------------------------------------
# ROCE
# --------------------------------------------------

def roce(ebit,
         equity_capital,
         reserves,
         borrowings):

    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return round((ebit / capital) * 100, 2)


# --------------------------------------------------
# ROA
# --------------------------------------------------

def roa(net_profit,
        total_assets):

    if total_assets == 0:
        return None

    return round((net_profit / total_assets) * 100, 2)


# --------------------------------------------------
# Financial Sector Benchmark
# --------------------------------------------------

def financial_sector_roce_check(roce_value,
                                broad_sector):

    if broad_sector == "Financials":
        return "Sector Relative"

    if roce_value is None:
        return "Invalid"

    if roce_value >= 15:
        return "Good"

    return "Needs Improvement"