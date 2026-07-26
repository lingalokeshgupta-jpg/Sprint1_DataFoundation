import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import sqlite3
import pandas as pd
import numpy as np

from screener.presets import presets
from screener.engine import apply_filters

conn = sqlite3.connect("db/nifty100.db")

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

sectors = pd.read_sql(
    "SELECT company_id, broad_sector FROM sectors",
    conn
)

merged = financial_ratios.merge(
    sectors,
    on="company_id",
    how="left"
)

print(merged.head())
print(merged.columns.tolist())

def winsorize(series):

    p10 = series.quantile(0.10)

    p90 = series.quantile(0.90)

    return series.clip(lower=p10, upper=p90)

def normalize(series):

    minimum = series.min()

    maximum = series.max()

    if maximum == minimum:
        return 50

    return (
        (series - minimum)
        /
        (maximum - minimum)
    ) * 100

score_columns = [

    "return_on_equity_pct",

    "net_profit_margin_pct",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "free_cash_flow_cr",

    "cash_from_operations_cr",

    "debt_to_equity",

    "interest_coverage"

]

# Winsorize all score columns
for col in score_columns:
    merged[col] = winsorize(merged[col])

# Normalize all score columns
for col in score_columns:
    merged[col] = normalize(merged[col])

# Invert Debt-to-Equity score (lower D/E = better)
merged["debt_to_equity"] = 100 - merged["debt_to_equity"]

# Replace remaining NaN values with 0
merged[score_columns] = merged[score_columns].fillna(0)
print(merged[score_columns].head())

print("\nNull Values:")
print(merged[score_columns].isnull().sum())

# ------------------------------------------
# Weighted Composite Score
# ------------------------------------------

merged["weighted_composite_score"] = (

    merged["return_on_equity_pct"] * 0.15 +

    merged["net_profit_margin_pct"] * 0.10 +

    merged["revenue_cagr_5yr"] * 0.10 +

    merged["pat_cagr_5yr"] * 0.10 +

    merged["free_cash_flow_cr"] * 0.15 +

    merged["cash_from_operations_cr"] * 0.10 +

    merged["debt_to_equity"] * 0.10 +

    merged["interest_coverage"] * 0.05

)

print("\nWeighted Composite Score")

print(
    merged[
        [
            "company_id",
            "year",
            "weighted_composite_score"
        ]
    ].head(10)
)

# ----------------------------------------
# Sector Relative Composite Score
# ----------------------------------------

merged["sector_relative_score"] = (
    merged.groupby("broad_sector")["weighted_composite_score"]
    .transform(normalize)
)

print("\nSector Relative Score")

print(
    merged[
        [
            "company_id",
            "broad_sector",
            "weighted_composite_score",
            "sector_relative_score"
        ]
    ].head(10)
)

# ------------------------------------------
# Export Screener Excel
# ------------------------------------------

output_folder = Path("output")
output_folder.mkdir(exist_ok=True)

writer = pd.ExcelWriter(
    output_folder / "screener_output.xlsx",
    engine="openpyxl"
)

for sheet_name, preset in presets.items():

    result = apply_filters(
        merged,
        preset
    )

    result = result.sort_values(
        by="sector_relative_score",
        ascending=False
    )

    result.to_excel(
        writer,
        sheet_name=sheet_name[:31],
        index=False
    )

writer.close()

print("\nScreener Excel generated successfully!")
print(output_folder / "screener_output.xlsx")

