import sqlite3
import pandas as pd
import sys
from pathlib import Path

# ----------------------------------------
# Add project paths
# ----------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "etl"))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "analytics"))

# ----------------------------------------
# Imports
# ----------------------------------------

from loader import load_all_files

# Analytics modules
from ratios import *
from cagr import *
from cashflow_kpis import *

# ----------------------------------------
# Load all datasets
# ----------------------------------------

dataframes = load_all_files()

print("\nDatasets Loaded Successfully\n")

for name in dataframes:
    print(name)

# ----------------------------------------
# Individual DataFrames
# ----------------------------------------

companies = dataframes["companies"]

profitandloss = dataframes["profitandloss"]

balancesheet = dataframes["balancesheet"]

cashflow = dataframes["cashflow"]

print("\nProfit & Loss Columns")
print(profitandloss.columns.tolist())

print("\nBalance Sheet Columns")
print(balancesheet.columns.tolist())

print("\nCash Flow Columns")
print(cashflow.columns.tolist())


# ----------------------------------------
# Merge Profit & Loss + Balance Sheet
# ----------------------------------------

merged = profitandloss.merge(
    balancesheet,
    on=["company_id", "year"],
    how="inner",
    suffixes=("_pl", "_bs")
)

print("\nAfter Profit & Loss + Balance Sheet Merge")
print(merged.shape)

# ----------------------------------------
# Merge Cash Flow
# ----------------------------------------

merged = merged.merge(
    cashflow,
    on=["company_id", "year"],
    how="inner"
)

print("\nAfter Cash Flow Merge")
print(merged.shape)

# ----------------------------------------
# Merge Companies
# ----------------------------------------

merged = merged.merge(
    companies,
    left_on="company_id",
    right_on="id",
    how="left",
    suffixes=("", "_company")
)

print("\nFinal Merged Dataset")
print(merged.shape)

print("\nMerged Columns:")
print(merged.columns.tolist())


# =====================================================
# PASTE THE KPI CALCULATION CODE HERE
# =====================================================

merged["net_profit_margin_pct"] = merged.apply(
    lambda row: net_profit_margin(
        row["net_profit"],
        row["sales"]
    ),
    axis=1
)

merged["operating_profit_margin_pct"] = merged.apply(
    lambda row: operating_profit_margin(
        row["operating_profit"],
        row["sales"]
    ),
    axis=1
)

merged["return_on_equity_pct"] = merged.apply(
    lambda row: roe(
        row["net_profit"],
        row["equity_capital"],
        row["reserves"]
    ),
    axis=1
)

merged["debt_to_equity"] = merged.apply(
    lambda row: debt_to_equity(
        row["borrowings"],
        row["equity_capital"],
        row["reserves"]
    ),
    axis=1
)

merged["interest_coverage"] = merged.apply(
    lambda row: interest_coverage_ratio(
        row["operating_profit"],
        row["other_income"],
        row["interest"]
    ),
    axis=1
)

merged["asset_turnover"] = merged.apply(
    lambda row: asset_turnover(
        row["sales"],
        row["total_assets"]
    ),
    axis=1
)

merged["free_cash_flow_cr"] = merged.apply(
    lambda row: free_cash_flow(
        row["operating_activity"],
        row["investing_activity"]
    ),
    axis=1
)

merged["capex_cr"] = merged.apply(
    lambda row: capex_intensity(
        row["investing_activity"],
        row["sales"]
    )[0],
    axis=1
)

merged["earnings_per_share"] = merged["eps"]

merged["book_value_per_share"] = merged["book_value"]

merged["dividend_payout_ratio_pct"] = merged["dividend_payout"]

merged["total_debt_cr"] = merged["borrowings"]

merged["cash_from_operations_cr"] = merged["operating_activity"]

# =====================================================
# 5-Year CAGR Calculation
# =====================================================

merged = merged.sort_values(
    ["company_id", "year"]
).reset_index(drop=True)

merged["revenue_cagr_5yr"] = None
merged["pat_cagr_5yr"] = None
merged["eps_cagr_5yr"] = None

for company, group in merged.groupby("company_id"):

    group = group.sort_values("year")

    for i in range(len(group)):

        if i < 5:
            continue

        start = group.iloc[i - 5]
        end = group.iloc[i]

        revenue_value, revenue_flag = revenue_cagr(
            start["sales"],
            end["sales"],
            5
        )

        pat_value, pat_flag = pat_cagr(
            start["net_profit"],
            end["net_profit"],
            5
        )

        eps_value, eps_flag = eps_cagr(
            start["eps"],
            end["eps"],
            5
        )

        merged.loc[end.name, "revenue_cagr_5yr"] = revenue_value
        merged.loc[end.name, "pat_cagr_5yr"] = pat_value
        merged.loc[end.name, "eps_cagr_5yr"] = eps_value


# =====================================================
# Composite Quality Score
# =====================================================

def quality_score(row):

    score = 0

    # ROE
    if row["return_on_equity_pct"] is not None and row["return_on_equity_pct"] >= 15:
        score += 2

    # Debt to Equity
    if row["debt_to_equity"] is not None and row["debt_to_equity"] <= 1:
        score += 2

    # Interest Coverage
    if row["interest_coverage"] is not None and row["interest_coverage"] >= 3:
        score += 2

    # Free Cash Flow
    if row["free_cash_flow_cr"] is not None and row["free_cash_flow_cr"] > 0:
        score += 2

    # Net Profit Margin
    if row["net_profit_margin_pct"] is not None and row["net_profit_margin_pct"] >= 10:
        score += 2

    return score


merged["composite_quality_score"] = merged.apply(
    quality_score,
    axis=1
)    

# =====================================================
# Populate financial_ratios Table
# =====================================================

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

# Remove existing records
cursor.execute("DELETE FROM financial_ratios")

# Prepare final dataframe
final_df = merged[
    [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]
]

# Insert into SQLite
final_df.to_sql(
    "financial_ratios",
    conn,
    if_exists="append",
    index=False
)

conn.commit()

print("\nfinancial_ratios table populated successfully!")

# =====================================================
# VERIFY THE OUTPUT
# =====================================================

print(
    merged[
        [
            "company_id",
            "year",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "composite_quality_score"
        ]
    ].tail(10)
)