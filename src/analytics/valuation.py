import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "db/nifty100.db"
)

companies = pd.read_sql(
    """
    SELECT
        id AS company_id,
        company_name
    FROM companies
    """,
    conn
)

financial_ratios = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    """,
    conn
)

sectors = pd.read_sql(
    """
    SELECT *
    FROM sectors
    """,
    conn
)

market_cap = pd.read_sql(
    """
    SELECT *
    FROM market_cap
    """,
    conn
)


merged = financial_ratios.merge(
    companies,
    on="company_id",
    how="left"
)

merged = merged.merge(
    sectors,
    on="company_id",
    how="left"
)

merged = merged.merge(
    market_cap,
    on="company_id",
    how="left"
)

print(merged.columns.tolist())

latest = (
    merged
    .sort_values("year_x")
    .groupby("company_id")
    .tail(1)
    .copy()
)

print(
    latest[
        [
            "company_id",
            "year_x"
        ]
    ].head()
)

latest["fcf_yield_pct"] = (
    latest["free_cash_flow_cr"]
    .div(latest["market_cap_crore"])
    .fillna(0)
) * 100

sector_median = (

    latest

    .groupby("broad_sector")["pe_ratio"]

    .median()

    .reset_index()

)

sector_median.columns = [

    "broad_sector",

    "sector_median_pe"

]

latest = latest.merge(

    sector_median,

    on="broad_sector",

    how="left"

)

latest["pe_vs_sector_median_pct"] = (

    latest["pe_ratio"]

    /

    latest["sector_median_pe"]

) * 100

def valuation_flag(row):

    if pd.isna(row["pe_ratio"]):
        return "N/A"

    if row["pe_ratio"] > row["sector_median_pe"] * 1.5:
        return "Caution"

    elif row["pe_ratio"] < row["sector_median_pe"] * 0.7:
        return "Discount"

    return "Fair"


latest["flag"] = latest.apply(
    valuation_flag,
    axis=1
)

print(

    latest[
        [
            "company_id",
            "broad_sector",
            "pe_ratio",
            "sector_median_pe",
            "fcf_yield_pct",
            "flag"
        ]
    ].head(10)


)

valuation_summary = latest[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "fcf_yield_pct",
        "sector_median_pe",
        "pe_vs_sector_median_pct",
        "flag"
    ]
].copy()

valuation_summary.columns = [
    "company_id",
    "company_name",
    "sector",
    "P/E",
    "P/B",
    "EV/EBITDA",
    "FCF_yield_pct",
    "Sector_Median_PE",
    "PE_vs_sector_median_pct",
    "flag"
]

valuation_summary.to_excel(
    "output/valuation_summary.xlsx",
    index=False
)

valuation_flags = valuation_summary[
    valuation_summary["flag"].isin(
        ["Caution", "Discount"]
    )
]

valuation_flags.to_csv(
    "output/valuation_flags.csv",
    index=False
)
print(merged.head())

print(companies.shape)
print(financial_ratios.shape)
print(sectors.shape)
print(market_cap.shape)
print("\n========== Valuation Module Completed ==========")
print(f"Total Companies Processed : {len(valuation_summary)}")
print(f"Flagged Companies         : {len(valuation_flags)}")
print("Generated Files:")
print("  ✔ output/valuation_summary.xlsx")
print("  ✔ output/valuation_flags.csv")
print("==============================================") 