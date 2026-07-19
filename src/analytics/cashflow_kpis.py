"""
Sprint 2 - Day 11
Cash Flow KPIs & Capital Allocation
"""

import pandas as pd


# --------------------------------------------------
# Free Cash Flow
# --------------------------------------------------

def free_cash_flow(operating_activity, investing_activity):
    """
    FCF = CFO + Investing Activity
    Negative values are allowed.
    """
    return operating_activity + investing_activity


# --------------------------------------------------
# CFO Quality Score
# --------------------------------------------------

def cfo_quality_score(cfo_values, pat_values):
    """
    Average CFO/PAT ratio over available years.
    """

    ratios = []

    for cfo, pat in zip(cfo_values, pat_values):

        if pat == 0:
            continue

        ratios.append(cfo / pat)

    if len(ratios) == 0:
        return None

    average = sum(ratios) / len(ratios)

    if average > 1:
        return "High Quality"

    if average >= 0.5:
        return "Moderate"

    return "Accrual Risk"


# --------------------------------------------------
# CapEx Intensity
# --------------------------------------------------

def capex_intensity(investing_activity, sales):

    if sales == 0:
        return None, None

    value = abs(investing_activity) / sales * 100

    if value < 3:
        label = "Asset Light"

    elif value <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(value, 2), label


# --------------------------------------------------
# FCF Conversion Rate
# --------------------------------------------------

def fcf_conversion_rate(fcf, operating_profit):

    if operating_profit == 0:
        return None

    return round(
        (fcf / operating_profit) * 100,
        2
    )


# --------------------------------------------------
# Capital Allocation Pattern
# --------------------------------------------------

def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=1):

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):

        if cfo_pat_ratio > 1:
            return "Shareholder Returns"

        return "Reinvestor"

    if signs == ("+", "+", "-"):
        return "Liquidating Assets"

    if signs == ("-", "+", "+"):
        return "Distress Signal"

    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if signs == ("+", "+", "+"):
        return "Cash Accumulator"

    if signs == ("-", "-", "-"):
        return "Pre-Revenue"

    if signs == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"


# --------------------------------------------------
# Generate CSV
# --------------------------------------------------

def generate_capital_allocation(df, output_path):

    result = pd.DataFrame()

    result["company_id"] = df["company_id"]
    result["year"] = df["year"]

    result["cfo_sign"] = df["operating_activity"].apply(
        lambda x: "+" if x >= 0 else "-"
    )

    result["cfi_sign"] = df["investing_activity"].apply(
        lambda x: "+" if x >= 0 else "-"
    )

    result["cff_sign"] = df["financing_activity"].apply(
        lambda x: "+" if x >= 0 else "-"
    )

    result["pattern_label"] = df.apply(
        lambda row:
        capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        ),
        axis=1
    )

    result.to_csv(output_path, index=False)

    return result

