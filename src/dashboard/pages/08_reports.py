import streamlit as st

from utils.db import get_companies

st.title("Annual Reports")

companies = get_companies()

ticker = st.selectbox(
    "Select Company",
    companies["id"]
)

company = companies[
    companies["id"] == ticker
].iloc[0]

st.subheader(company["company_name"])

years = [
    "2024",
    "2023",
    "2022",
    "2021",
    "2020"
]

st.subheader("Available Reports")

for year in years:

    st.write(year)


for year in years:

    st.button(
        f"Open {year} Report",
        key=year
    )

st.error("Report Unavailable")

st.link_button(
    "Open Annual Report",
    company["bse_profile"]
)