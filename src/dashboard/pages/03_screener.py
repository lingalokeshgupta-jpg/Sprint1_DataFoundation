import streamlit as st
import pandas as pd

from utils.db import (
    get_all_ratios,
    get_companies,
    get_sectors
)

st.title("🔍 Stock Screener")

ratios = get_all_ratios()

companies = get_companies()

sectors = get_sectors()

screen = ratios.merge(
    companies,
    left_on="company_id",
    right_on="id",
    how="left"
)

screen = screen.merge(
    sectors,
    on="company_id",
    how="left"
)

st.sidebar.subheader("Presets")

quality = st.sidebar.button("Quality")
value = st.sidebar.button("Value")
growth = st.sidebar.button("Growth")
dividend = st.sidebar.button("Dividend")
debtfree = st.sidebar.button("Debt-Free")
turnaround = st.sidebar.button("Turnaround")

if quality:
    st.success("Quality preset selected")

if value:
    st.success("Value preset selected")

if growth:
    st.success("Growth preset selected")

if dividend:
    st.success("Dividend preset selected")

if debtfree:
    st.success("Debt-Free preset selected")

if turnaround:
    st.success("Turnaround preset selected")
    
st.sidebar.header("Filters")

roe = st.sidebar.slider(
    "Minimum ROE",
    0,
    50,
    15
)

de = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    10.0,
    1.0
)

fcf = st.sidebar.number_input(
    "Minimum Free Cash Flow",
    value=0
)

revenue = st.sidebar.slider(
    "Revenue CAGR",
    0,
    50,
    10
)

pat = st.sidebar.slider(
    "PAT CAGR",
    0,
    50,
    10
)

opm = st.sidebar.slider(
    "Operating Profit Margin",
    0,
    50,
    10
)

pe = st.sidebar.number_input(
    "Maximum PE",
    value=20
)

pb = st.sidebar.number_input(
    "Maximum PB",
    value=3
)

dividend = st.sidebar.number_input(
    "Minimum Dividend Yield",
    value=1
)

icr = st.sidebar.number_input(
    "Minimum Interest Coverage",
    value=3
)

filtered = screen[
    (screen["return_on_equity_pct"] >= roe) &
    (screen["debt_to_equity"] <= de) &
    (screen["free_cash_flow_cr"] >= fcf) &
    (screen["revenue_cagr_5yr"] >= revenue) &
    (screen["pat_cagr_5yr"] >= pat) &
    (screen["operating_profit_margin_pct"] >= opm) &
    (screen["interest_coverage"] >= icr)
]

st.subheader(f"{len(filtered)} companies match your filters")

display = filtered[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "composite_quality_score",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "interest_coverage"
    ]
]

st.dataframe(
    display,
    use_container_width=True
)

csv = display.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="screener_results.csv",
    mime="text/csv"
)