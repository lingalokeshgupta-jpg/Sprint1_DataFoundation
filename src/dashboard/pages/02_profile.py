import streamlit as st
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
    get_pl
)

st.title("🏢 Company Profile")

companies = get_companies()

sectors = get_sectors()

ticker = st.selectbox(
    "Select Company",
    companies["id"]
)

ratios = get_ratios(ticker)

pl = get_pl(ticker)

company = companies[
    companies["id"] == ticker
]

ratio = ratios[
    ratios["company_id"] == ticker
]

sector = sectors[
    sectors["company_id"] == ticker
]

if company.empty or ratio.empty or sector.empty:
    st.warning("Ticker not found — please try another.")
    st.stop()

latest = ratio.sort_values(
    "year"
).iloc[-1]

st.markdown(f"""
### {company.iloc[0]["company_name"]}

**Ticker:** {ticker}

**Sector:** {sector.iloc[0]["broad_sector"]}

{company.iloc[0]["about_company"]}
""")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "ROE",
    round(latest["return_on_equity_pct"], 2)
)

col2.metric(
    "Net Profit Margin",
    round(latest["net_profit_margin_pct"], 2)
)

col3.metric(
    "Debt / Equity",
    round(latest["debt_to_equity"], 2)
)

col4.metric(
    "Revenue CAGR",
    round(latest["revenue_cagr_5yr"], 2)
)

col5.metric(
    "Free Cash Flow",
    round(latest["free_cash_flow_cr"], 2)
)

col6.metric(
    "Composite Score",
    round(latest["composite_quality_score"], 2)
)

st.subheader("Revenue vs Net Profit (10 Years)")

fig = px.bar(
    pl,
    x="year",
    y=["sales", "net_profit"],
    barmode="group",
    title="Revenue and Net Profit"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Cash Flow Trend")

fig = px.bar(
    ratio,
    x="year",
    y="cash_from_operations_cr",
    title="Cash From Operations"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("ROE Trend")

fig = px.line(
    ratio,
    x="year",
    y="return_on_equity_pct",
    markers=True,
    title="ROE Over Time"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Pros")

if latest["return_on_equity_pct"] > 15:
    st.success("High Return on Equity")

if latest["debt_to_equity"] < 1:
    st.success("Low Debt")

if latest["free_cash_flow_cr"] > 0:
    st.success("Positive Free Cash Flow")

st.subheader("Cons")

if latest["debt_to_equity"] > 2:
    st.error("High Debt")

if latest["revenue_cagr_5yr"] < 5:
    st.error("Low Revenue Growth")

if latest["free_cash_flow_cr"] < 0:
    st.error("Negative Free Cash Flow")