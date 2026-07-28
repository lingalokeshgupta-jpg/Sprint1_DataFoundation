import streamlit as st
import plotly.express as px
import pandas as pd

from utils.db import (
    get_all_ratios,
    get_companies
)

st.title("🌳Capital Allocation")

ratios = get_all_ratios()

companies = get_companies()

latest = ratios.sort_values("year").groupby("company_id").tail(1)

latest = latest.merge(
    companies[
        ["id", "company_name"]
    ],
    left_on="company_id",
    right_on="id",
    how="left"
)

def capital_pattern(row):

    if row["debt_to_equity"] < 0.5 and row["free_cash_flow_cr"] > 0:
        return "Debt Free"

    elif row["revenue_cagr_5yr"] > 15:
        return "Growth"

    elif row["dividend_payout_ratio_pct"] > 40:
        return "Dividend"

    elif row["capex_cr"] > row["free_cash_flow_cr"]:
        return "Heavy CapEx"

    elif row["return_on_equity_pct"] > 20:
        return "Quality"

    elif row["interest_coverage"] < 2:
        return "Highly Leveraged"

    elif row["asset_turnover"] > 1:
        return "Efficient"

    else:
        return "Balanced"

latest["capital_pattern"] = latest.apply(
    capital_pattern,
    axis=1
)

fig = px.treemap(
    latest,
    path=["capital_pattern", "company_id"],
    values="free_cash_flow_cr",
    color="return_on_equity_pct",
    hover_data=["company_name"]
)

st.plotly_chart(
    fig,
    use_container_width=True
)

pattern = st.selectbox(
    "Select Pattern",
    sorted(
        latest["capital_pattern"].unique()
    )
)

filtered = latest[
    latest["capital_pattern"] == pattern
]

st.subheader("Companies")

st.dataframe(
    filtered[
        [
            "company_id",
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr"
        ]
    ],
    use_container_width=True
)