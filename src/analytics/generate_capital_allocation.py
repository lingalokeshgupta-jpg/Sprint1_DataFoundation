import sys
from pathlib import Path


# --------------------------------------------------
# PROJECT ROOT
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------
# MAKE PROJECT MODULES IMPORTABLE
# --------------------------------------------------

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "etl"))


from loader import load_all_files
from src.analytics.cashflow_kpis import generate_capital_allocation


# --------------------------------------------------
# LOAD DATASETS
# --------------------------------------------------

dataframes = load_all_files()

cashflow_df = dataframes["cashflow"].copy()


# --------------------------------------------------
# NORMALIZE YEAR FORMAT
# --------------------------------------------------

def normalize_year(value):

    value = str(value).strip()

    # Convert Mar-13 → Mar 2013
    if value.startswith("Mar-"):

        year = value.replace("Mar-", "")

        if len(year) == 2:

            year_num = int(year)

            if year_num >= 50:
                year_num += 1900
            else:
                year_num += 2000

            return f"Mar {year_num}"

    return value


cashflow_df["year"] = cashflow_df["year"].apply(
    normalize_year
)


# --------------------------------------------------
# REMOVE DUPLICATE COMPANY-YEAR RECORDS
# --------------------------------------------------

before = len(cashflow_df)

cashflow_df = cashflow_df.drop_duplicates(
    subset=[
        "company_id",
        "year"
    ],
    keep="first"
).copy()

removed = before - len(cashflow_df)


print(
    "Duplicate company-year records removed:",
    removed
)


# --------------------------------------------------
# VERIFY DUPLICATES
# --------------------------------------------------

duplicates = cashflow_df[
    cashflow_df.duplicated(
        subset=[
            "company_id",
            "year"
        ],
        keep=False
    )
]


if duplicates.empty:

    print(
        "Verification: NO duplicate company-year records."
    )

else:

    print(
        "WARNING: Duplicate company-year records remain:"
    )

    print(duplicates)


# --------------------------------------------------
# GENERATE CAPITAL ALLOCATION
# --------------------------------------------------

generate_capital_allocation(
    cashflow_df,
    "output/capital_allocation.csv"
)


print(
    "capital_allocation.csv created successfully."
)