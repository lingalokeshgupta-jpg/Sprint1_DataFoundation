import streamlit as st
import plotly.express as px
import pandas as pd

from utils.db import (
    get_all_ratios,
    get_sectors
)

st.title("📊 Sector Analysis")

ratios = get_all_ratios()

sectors = get_sectors()

sector_df = ratios.merge(
    sectors,
    on="company_id",
    how="left"
)

sector_name = st.selectbox(
    "Select Sector",
    sorted(
        sector_df["broad_sector"].dropna().unique()
    )
)

sector_data = sector_df[
    sector_df["broad_sector"] == sector_name
].copy()

sector_data["bubble_size"] = (
    sector_data["free_cash_flow_cr"]
    .abs()
    .replace(0, 1)
)

fig = px.scatter(
    sector_data,
    x="revenue_cagr_5yr",
    y="return_on_equity_pct",
    size="bubble_size",
    color="broad_sector",
    hover_name="company_id",
    title=f"{sector_name} Sector Analysis"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

median = sector_data[
    [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "free_cash_flow_cr"
    ]
].median()

median_df = median.reset_index()

median_df.columns = [
    "Metric",
    "Median"
]

fig = px.bar(
    median_df,
    x="Metric",
    y="Median",
    title="Sector Median KPIs"
)

st.plotly_chart(
    fig,
    use_container_width=True
)