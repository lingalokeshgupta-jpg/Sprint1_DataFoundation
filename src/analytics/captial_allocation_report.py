"""import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

capital = pd.read_csv(
    "output/capital_allocation.csv"
)

conn = sqlite3.connect(DB_PATH)

companies = pd.read_sql(
    "SELECT id FROM companies",
    conn
)

conn.close()

print("=" * 50)
print("CAPITAL ALLOCATION VERIFICATION")
print("=" * 50)

print("Companies table :", companies["id"].nunique())
print("Capital allocation companies :", capital["company_id"].nunique())
print("Capital allocation rows :", len(capital))


missing_companies = sorted(
    set(companies["id"]) -
    set(capital["company_id"])
)

print("\nMissing companies:")

if missing_companies:
    print(missing_companies)
else:
    print("None")

print(
    "Missing count:",
    len(missing_companies)
)

duplicates = capital[
    capital.duplicated(
        subset=["company_id", "year"],
        keep=False
    )
]

print("\nDuplicate company-year records:")

if duplicates.empty:
    print("None")
else:
    print(duplicates)


print("\nCapital Allocation Patterns:")
print(
    capital["pattern_label"]
    .value_counts()
)


latest_year = capital["year"].max()

print("\nLatest Year:", latest_year)

latest = capital[
    capital["year"] == latest_year
].copy()

distribution = (
    latest["pattern_label"]
    .value_counts()
    .reindex(
        [
            "Shareholder Returns",
            "Reinvestor",
            "Liquidating Assets",
            "Distress Signal",
            "Growth Funded by Debt",
            "Cash Accumulator",
            "Pre-Revenue",
            "Mixed"
        ],
        fill_value=0
    )
    .reset_index()
)

distribution.columns = [
    "pattern_label",
    "company_count"
]

print("\nLatest Year Distribution:")
print(distribution)

distribution.to_csv(
    "output/capital_allocation_distribution.csv",
    index=False
)

print(
    "\nSaved: output/capital_allocation_distribution.csv"
)


capital = capital.sort_values(
    ["company_id", "year"]
)

capital["previous_pattern"] = (
    capital
    .groupby("company_id")["pattern_label"]
    .shift(1)
)

capital["previous_year"] = (
    capital
    .groupby("company_id")["year"]
    .shift(1)
)


changes = capital[
    capital["previous_pattern"].notna()
    &
    (
        capital["pattern_label"]
        !=
        capital["previous_pattern"]
    )
].copy()

pattern_changes = changes[
    [
        "company_id",
        "previous_year",
        "year",
        "previous_pattern",
        "pattern_label"
    ]
].copy()

pattern_changes.columns = [
    "company_id",
    "previous_year",
    "current_year",
    "previous_pattern",
    "current_pattern"
]

pattern_changes.to_csv(
    "output/pattern_changes.csv",
    index=False
)

print(
    "Saved: output/pattern_changes.csv"
)

cashflow_intelligence = pd.read_excel(
    "output/cashflow_intelligence.xlsx"
)

latest_allocation = (
    capital
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
    [
        [
            "company_id",
            "pattern_label"
        ]
    ]
)

latest_allocation = latest_allocation.rename(
    columns={
        "pattern_label": "capital_allocation_label"
    }
)

cashflow_intelligence = cashflow_intelligence.drop(
    columns=["capital_allocation_label"],
    errors="ignore"
)

cashflow_intelligence = cashflow_intelligence.merge(
    latest_allocation,
    on="company_id",
    how="left"
)

cashflow_intelligence.to_excel(
    "output/cashflow_intelligence.xlsx",
    index=False
)

print(
    "Updated: output/cashflow_intelligence.xlsx"
)

print("\nCash Flow Intelligence:")
print(
    cashflow_intelligence.shape
)

print(
    cashflow_intelligence.columns.tolist()
)

print(
    "Companies:",
    cashflow_intelligence["company_id"].nunique()
)


print("\n" + "=" * 50)
print("DAY 32 CAPITAL ALLOCATION REPORT")
print("=" * 50)

print(
    "Companies in allocation:",
    capital["company_id"].nunique()
)

print(
    "Latest year:",
    latest_year
)

print(
    "Latest-year companies:",
    len(latest)
)

print(
    "Pattern changes:",
    len(pattern_changes)
)

print("\nGenerated files:")
print("✓ output/capital_allocation_distribution.csv")
print("✓ output/pattern_changes.csv")
print("✓ output/cashflow_intelligence.xlsx")"""

import sqlite3
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = "db/nifty100.db"

CAPITAL_FILE = "output/capital_allocation.csv"

CASHFLOW_INTELLIGENCE_FILE = (
    "output/cashflow_intelligence.xlsx"
)


# ============================================================
# LOAD DATABASE COMPANIES
# ============================================================

conn = sqlite3.connect(DB_PATH)

companies = pd.read_sql(
    "SELECT id FROM companies",
    conn
)

conn.close()


# ============================================================
# LOAD CAPITAL ALLOCATION
# ============================================================

capital = pd.read_csv(
    CAPITAL_FILE
)

print("=" * 60)
print("DAY 32 - CAPITAL ALLOCATION REPORT")
print("=" * 60)


# ============================================================
# BASIC VALIDATION
# ============================================================

print("\n========== BASIC VERIFICATION ==========")

print(
    "Companies table:",
    companies["id"].nunique()
)

print(
    "Capital allocation companies:",
    capital["company_id"].nunique()
)

print(
    "Capital allocation rows:",
    len(capital)
)


# ============================================================
# KEEP ONLY CURRENT 92 COMPANIES
# ============================================================

company_ids = set(
    companies["id"].astype(str).str.strip()
)

capital["company_id"] = (
    capital["company_id"]
    .astype(str)
    .str.strip()
)

capital_current = capital[
    capital["company_id"].isin(company_ids)
].copy()


print(
    "\nCapital allocation rows for current companies:",
    len(capital_current)
)

print(
    "Current companies with allocation data:",
    capital_current["company_id"].nunique()
)


# ============================================================
# FIND MISSING COMPANIES
# ============================================================

missing_companies = sorted(
    company_ids -
    set(capital_current["company_id"])
)

print("\n========== MISSING COMPANIES ==========")

if missing_companies:
    print(missing_companies)
else:
    print("None")

print(
    "Missing count:",
    len(missing_companies)
)


# ============================================================
# CONVERT YEAR TO DATE
# ============================================================

capital_current["year_date"] = pd.to_datetime(
    capital_current["year"],
    format="%b %Y",
    errors="coerce"
)


invalid_dates = capital_current[
    capital_current["year_date"].isna()
]

if not invalid_dates.empty:

    print("\nWARNING: Invalid year values found:")
    print(
        invalid_dates[
            ["company_id", "year"]
        ].drop_duplicates()
    )

else:

    print(
        "\nAll year values converted successfully."
    )


# ============================================================
# CHECK DUPLICATE COMPANY + YEAR
# ============================================================

duplicates = capital_current[
    capital_current.duplicated(
        subset=[
            "company_id",
            "year_date"
        ],
        keep=False
    )
].copy()


print("\n========== DUPLICATE CHECK ==========")

if duplicates.empty:

    print(
        "No duplicate company-year records."
    )

else:

    print(
        "Duplicate company-year records found:",
        len(duplicates)
    )

    print(
        duplicates[
            [
                "company_id",
                "year",
                "pattern_label"
            ]
        ].to_string(index=False)
    )

    print(
        "\nIMPORTANT:"
        "\nThese duplicates must be resolved in "
        "capital_allocation.csv before the final "
        "Day 32 report can be considered fully valid."
    )


# ============================================================
# DO NOT SILENTLY USE DUPLICATES
# ============================================================
#
# For reporting purposes we keep the first record only
# so that the report can be generated.
#
# The duplicate issue should still be documented because
# the underlying capital allocation data needs correction.
# ============================================================

capital_clean = (
    capital_current
    .sort_values(
        [
            "company_id",
            "year_date"
        ]
    )
    .drop_duplicates(
        subset=[
            "company_id",
            "year_date"
        ],
        keep="first"
    )
    .copy()
)


# ============================================================
# 8 CAPITAL ALLOCATION PATTERNS
# ============================================================

patterns = [
    "Shareholder Returns",
    "Reinvestor",
    "Liquidating Assets",
    "Distress Signal",
    "Growth Funded by Debt",
    "Cash Accumulator",
    "Pre-Revenue",
    "Mixed"
]


print("\n========== PATTERN COUNTS ==========")

pattern_counts = (
    capital_clean["pattern_label"]
    .value_counts()
)

print(pattern_counts)


# ============================================================
# LATEST AVAILABLE YEAR PER COMPANY
# ============================================================

latest_per_company = (
    capital_clean
    .sort_values(
        [
            "company_id",
            "year_date"
        ]
    )
    .groupby(
        "company_id",
        as_index=False
    )
    .tail(1)
    .copy()
)


print(
    "\nLatest records per company:",
    len(latest_per_company)
)

print(
    "Companies represented:",
    latest_per_company[
        "company_id"
    ].nunique()
)


# ============================================================
# LATEST-YEAR DISTRIBUTION
# ============================================================

distribution = (
    latest_per_company[
        "pattern_label"
    ]
    .value_counts()
    .reindex(
        patterns,
        fill_value=0
    )
    .reset_index()
)

distribution.columns = [
    "pattern_label",
    "company_count"
]


print(
    "\n========== LATEST PATTERN DISTRIBUTION =========="
)

print(distribution)


distribution.to_csv(
    "output/capital_allocation_distribution.csv",
    index=False
)

print(
    "\nSaved:"
    " output/capital_allocation_distribution.csv"
)


# ============================================================
# YEAR-OVER-YEAR PATTERN CHANGES
# ============================================================

capital_clean = capital_clean.sort_values(
    [
        "company_id",
        "year_date"
    ]
).copy()


capital_clean["previous_pattern"] = (
    capital_clean
    .groupby("company_id")[
        "pattern_label"
    ]
    .shift(1)
)


capital_clean["previous_year"] = (
    capital_clean
    .groupby("company_id")[
        "year_date"
    ]
    .shift(1)
)


changes = capital_clean[
    capital_clean["previous_pattern"].notna()
    &
    (
        capital_clean["pattern_label"]
        !=
        capital_clean["previous_pattern"]
    )
].copy()


pattern_changes = changes[
    [
        "company_id",
        "previous_year",
        "year_date",
        "previous_pattern",
        "pattern_label"
    ]
].copy()


pattern_changes.columns = [
    "company_id",
    "previous_year",
    "current_year",
    "previous_pattern",
    "current_pattern"
]


pattern_changes[
    "previous_year"
] = pattern_changes[
    "previous_year"
].dt.strftime("%b %Y")


pattern_changes[
    "current_year"
] = pattern_changes[
    "current_year"
].dt.strftime("%b %Y")


pattern_changes.to_csv(
    "output/pattern_changes.csv",
    index=False
)


print(
    "\nPattern changes:",
    len(pattern_changes)
)

print(
    "Saved: output/pattern_changes.csv"
)


# ============================================================
# UPDATE CASH FLOW INTELLIGENCE
# ============================================================

cashflow_intelligence = pd.read_excel(
    CASHFLOW_INTELLIGENCE_FILE
)


latest_allocation = latest_per_company[
    [
        "company_id",
        "pattern_label"
    ]
].copy()


latest_allocation = latest_allocation.rename(
    columns={
        "pattern_label":
        "capital_allocation_label"
    }
)


# Remove existing column if present

cashflow_intelligence = (
    cashflow_intelligence
    .drop(
        columns=[
            "capital_allocation_label"
        ],
        errors="ignore"
    )
)


# Merge latest allocation

cashflow_intelligence = (
    cashflow_intelligence
    .merge(
        latest_allocation,
        on="company_id",
        how="left"
    )
)


# Save updated Excel

cashflow_intelligence.to_excel(
    CASHFLOW_INTELLIGENCE_FILE,
    index=False
)


print(
    "\nUpdated:",
    CASHFLOW_INTELLIGENCE_FILE
)


# ============================================================
# FINAL VERIFICATION
# ============================================================

print("\n" + "=" * 60)
print("DAY 32 FINAL VERIFICATION")
print("=" * 60)

print(
    "Companies in database:",
    companies["id"].nunique()
)

print(
    "Companies with capital allocation:",
    capital_current[
        "company_id"
    ].nunique()
)

print(
    "Missing companies:",
    len(missing_companies)
)

print(
    "Duplicate company-year records:",
    len(duplicates)
)

print(
    "Latest records:",
    len(latest_per_company)
)

print(
    "Pattern changes:",
    len(pattern_changes)
)

print(
    "Cashflow intelligence shape:",
    cashflow_intelligence.shape
)


print("\nGenerated files:")

print(
    "✓ output/capital_allocation_distribution.csv"
)

print(
    "✓ output/pattern_changes.csv"
)

print(
    "✓ output/cashflow_intelligence.xlsx"
)


# ============================================================
# STATUS
# ============================================================

if (
    len(missing_companies) == 0
    and len(duplicates) == 0
    and
    latest_per_company["company_id"].nunique()
    == companies["id"].nunique()
):

    print(
        "\nDAY 32 STATUS: COMPLETE"
    )

else:

    print(
        "\nDAY 32 STATUS: DATA ISSUES REQUIRE ATTENTION"
    )

    if missing_companies:
        print(
            "- Missing companies:",
            missing_companies
        )

    if not duplicates.empty:
        print(
            "- Duplicate company-year records:",
            len(duplicates)
        )