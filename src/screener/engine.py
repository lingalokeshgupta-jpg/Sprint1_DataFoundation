import sqlite3
import pandas as pd
import yaml
from pathlib import Path

CONFIG_PATH = Path("config/screener_config.yaml")

with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)

print(config)

conn = sqlite3.connect("db/nifty100.db")

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print(financial_ratios.head())



def apply_filters(df, filters):
    filtered = df.copy()

    if filters.get("roe_min") is not None:
        filtered = filtered[
        filtered["return_on_equity_pct"]
        >= filters["roe_min"]
    ]


    if filters.get("free_cash_flow_min") is not None:
        filtered = filtered[
            filtered["free_cash_flow_cr"] >= filters["free_cash_flow_min"]
        ]

    if filters.get("revenue_cagr_5yr_min") is not None:
        filtered = filtered[
            filtered["revenue_cagr_5yr"] >= filters["revenue_cagr_5yr_min"]
        ]

    if filters.get("pat_cagr_5yr_min") is not None:
        filtered = filtered[
            filtered["pat_cagr_5yr"] >= filters["pat_cagr_5yr_min"]
        ]

    if filters.get("operating_profit_margin_min") is not None:
        filtered = filtered[
            filtered["operating_profit_margin_pct"] >= filters["operating_profit_margin_min"]
        ]

    if filters.get("interest_coverage_min") is not None:

        filtered["interest_coverage"] = filtered["interest_coverage"].replace(
            "Debt Free",
             float("inf")
        )

        filtered = filtered[
            filtered["interest_coverage"] >= filters["interest_coverage_min"]
        ]

    if filters.get("eps_cagr_5yr_min") is not None:
        filtered = filtered[
        filtered["eps_cagr_5yr"] >= filters["eps_cagr_5yr_min"]
        ]

    if filters.get("asset_turnover_min") is not None:
        filtered = filtered[
            filtered["asset_turnover"] >= filters["asset_turnover_min"]
    ]

    filtered = filtered.sort_values(
        by="composite_quality_score",
        ascending=False
    )

    return filtered


filtered_df = apply_filters(
    financial_ratios,
    config["filters"]
)

print("Original Rows :", financial_ratios.shape)
print("Filtered Rows :", filtered_df.shape)

print(filtered_df.head())

conn.close()

