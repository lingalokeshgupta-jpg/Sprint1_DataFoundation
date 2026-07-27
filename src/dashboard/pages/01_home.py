import plotly.express as px
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_sectors,
    get_all_ratios
)

st.title("🏠 Home Dashboard")

year = st.sidebar.selectbox(
    "Select Year",
    [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024"
    ]
)

# Load data
ratios = get_all_ratios()

companies = get_companies()

sectors = get_sectors()

# Filter data for selected year
ratios = ratios[
    ratios["year"] == year
]

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Average ROE",
    round(
        ratios["return_on_equity_pct"].mean(),
        2
    )
)

col2.metric(
    "Average Quality Score",
    round(
        ratios["composite_quality_score"].mean(),
        2
    )
)

col3.metric(
    "Median D/E",
    round(
        ratios["debt_to_equity"].median(),
        2
    )
)

col4.metric(
    "Total Companies",
    companies["id"].nunique()
)

col5.metric(
    "Median Revenue CAGR",
    round(
        ratios["revenue_cagr_5yr"].median(),
        2
    )
)

debt_free = ratios[
    ratios["debt_to_equity"] == 0
].shape[0]

col6.metric(
    "Debt-Free Companies",
    debt_free
)

sector_count = (
    sectors
    .groupby("broad_sector")
    .size()
    .reset_index(name="Companies")
)

fig = px.pie(
    sector_count,
    values="Companies",
    names="broad_sector",
    hole=0.5,
    title="Sector Breakdown"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

top5 = (
    ratios
    .sort_values(
        "composite_quality_score",
        ascending=False
    )
    [["company_id","composite_quality_score"]]
    .head(5)
)

st.subheader(
    "Top 5 Companies by Composite Score"
)

st.dataframe(
    top5,
    use_container_width=True
)