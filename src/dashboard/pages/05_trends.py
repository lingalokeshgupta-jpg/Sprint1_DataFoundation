import streamlit as st
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios
)

st.title("📈 Trends Analysis")

companies = get_companies()

ticker = st.selectbox(
    "Select Company",
    companies["id"]
)

ratios = get_ratios(ticker)

if ratios.empty:
    st.warning("No data available.")
    st.stop()

ratios = ratios.sort_values("year")

metrics = st.multiselect(
    "Select up to 3 Metrics",
    [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "interest_coverage",
        "asset_turnover"
    ],
    default=["return_on_equity_pct"],
    max_selections=3
)

fig = px.line(
    ratios,
    x="year",
    y=metrics,
    markers=True,
    title=f"{ticker} Trend Analysis"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

trend = ratios.copy()

for metric in metrics:
    trend[f"{metric}_YoY"] = (
        trend[metric]
        .pct_change()
        * 100
    )

st.subheader("Year-over-Year Change (%)")

columns = [
    "year"
]

for metric in metrics:
    columns.append(f"{metric}_YoY")

st.dataframe(
    trend[columns].round(2),
    use_container_width=True
)