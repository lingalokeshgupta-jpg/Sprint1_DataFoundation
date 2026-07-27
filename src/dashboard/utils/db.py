import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=600)
def get_companies():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM companies", conn)


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    conn = get_connection()

    query = """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    """

    params = [ticker]

    if year is not None:
        query += " AND year = ?"
        params.append(year)

    return pd.read_sql(
        query,
        conn,
        params=params
    )


@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = get_connection()

    query = """
    SELECT *
    FROM profitandloss
    WHERE company_id = ?
    """

    return pd.read_sql(
        query,
        conn,
        params=[ticker]
    )


@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = get_connection()

    query = """
    SELECT *
    FROM balancesheet
    WHERE company_id = ?
    """

    return pd.read_sql(
        query,
        conn,
        params=[ticker]
    )


@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = get_connection()

    query = """
    SELECT *
    FROM cashflow
    WHERE company_id = ?
    """

    return pd.read_sql(
        query,
        conn,
        params=[ticker]
    )


@st.cache_data(ttl=600)
def get_sectors():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM sectors", conn)


@st.cache_data(ttl=600)
def get_peers(group_name=None):

    conn = get_connection()

    if group_name is None:
        return pd.read_sql(
            "SELECT * FROM peer_groups",
            conn
        )

    query = """
    SELECT *
    FROM peer_groups
    WHERE peer_group_name = ?
    """

    return pd.read_sql(
        query,
        conn,
        params=[group_name]
    )


@st.cache_data(ttl=600)
def get_valuation(ticker):

    conn = get_connection() 

    query = """
    SELECT *
    FROM market_cap
    WHERE company_id = ?
    """

    return pd.read_sql(
        query,
        conn,
        params=[ticker]
    )

@st.cache_data(ttl=600)
def get_all_ratios():

    conn = get_connection()

    return pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

