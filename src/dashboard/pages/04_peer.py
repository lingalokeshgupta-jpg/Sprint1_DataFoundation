import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import (
    get_peers,
    get_ratios,
    get_sectors
)

st.title("👥 Peer Comparison")

peer_groups = get_peers()

peer_name = st.selectbox(

    "Select Peer Group",

    sorted(
        peer_groups["peer_group_name"].unique()
    )

)

group = peer_groups[
    peer_groups["peer_group_name"] == peer_name
]

company = st.selectbox(

    "Select Company",

    group["company_id"]

)

ratios = get_ratios(company)

if ratios.empty:

    st.warning(
        "No financial data available."
    )

    st.stop()

latest = ratios.iloc[-1]

metrics = [
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "composite_quality_score"
]

peer_companies = group["company_id"].tolist()

peer_ratios = []

for ticker in peer_companies:

    data = get_ratios(ticker)

    if not data.empty:

        peer_ratios.append(data.iloc[-1])

peer_df = pd.DataFrame(peer_ratios)

peer_average = peer_df[metrics].mean()

company_values = latest[metrics].fillna(0).tolist()

peer_values = peer_average.fillna(0).tolist()

fig = go.Figure()

labels = [
    "ROE",
    "OPM",
    "D/E",
    "FCF",
    "PAT CAGR",
    "Revenue CAGR",
    "EPS CAGR",
    "Composite Score"
]

fig.add_trace(

    go.Scatterpolar(

        r=company_values,

        theta=labels,

        fill="toself",

        name=company

    )

)

fig.add_trace(

    go.Scatterpolar(

        r=peer_values,

        theta=labels,

        line=dict(dash="dash"),

        name="Peer Average"

    )

)

fig.update_layout(

    polar=dict(

        radialaxis=dict(

            visible=True

        )

    ),

    showlegend=True,

    height=700

)

st.plotly_chart(

    fig,

    use_container_width=True

)

display = peer_df[
    [
        "company_id",
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "pat_cagr_5yr",
        "revenue_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]
]

display = display.merge(

    group[
        [
            "company_id",
            "is_benchmark"
        ]
    ],

    on="company_id",

    how="left"

)

st.subheader("Peer Comparison Table")

def highlight_benchmark(row):

    if row["is_benchmark"] == 1:
        return ["background-color: gold"] * len(row)

    return [""] * len(row)

styled = display.style.apply(
    highlight_benchmark,
    axis=1
)

st.dataframe(
    styled.hide(
        subset=["is_benchmark"],
        axis="columns"
    ),
    use_container_width=True
)

benchmark = group[
    group["is_benchmark"] == 1
]

if not benchmark.empty:

    st.success(
        f"Benchmark Company : {benchmark.iloc[0]['company_id']}"
    )


