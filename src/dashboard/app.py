import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Nifty 100 Analytics")

st.sidebar.title("Navigation")
st.sidebar.info("Select a page from the sidebar.")

st.write("Welcome to the Nifty 100 Analytics Dashboard")