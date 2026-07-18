import pandas as pd
from pathlib import Path
from loader import load_all_files
from datetime import datetime

# Output folder
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

validation_errors = []


def log_failure(rule, severity, table, message):
    validation_errors.append({
        "DQ_Rule": rule,
        "Severity": severity,
        "Table": table,
        "Message": message
    })


def save_failures():
    df = pd.DataFrame(validation_errors)

    if df.empty:
        print("No validation failures found.")
    else:
        df.to_csv(OUTPUT / "validation_failures.csv", index=False)
        print("validation_failures.csv created successfully.")


# ----------------------------------------------------
# DQ-01 Primary Key Uniqueness
# ----------------------------------------------------
def dq01_pk_uniqueness(df, pk_column, table):

    duplicates = df[df[pk_column].duplicated()]

    if not duplicates.empty:
        log_failure(
            "DQ-01",
            "CRITICAL",
            table,
            f"Duplicate values found in '{pk_column}'"
        )


# ----------------------------------------------------
# DQ-02 Foreign Key Integrity
# ----------------------------------------------------
def dq02_fk_integrity(child_df, parent_df, fk_column, pk_column, table):

    invalid = child_df[
        ~child_df[fk_column].isin(parent_df[pk_column])
    ]

    if not invalid.empty:
        log_failure(
            "DQ-02",
            "CRITICAL",
            table,
            f"{len(invalid)} invalid foreign keys in '{fk_column}'"
        )


# ----------------------------------------------------
# DQ-03 Missing Values
# ----------------------------------------------------
def dq03_missing_values(df, table):

    missing = df.isnull().sum().sum()

    if missing > 0:
        log_failure(
            "DQ-03",
            "CRITICAL",
            table,
            f"{missing} missing values found"
        )


# ----------------------------------------------------
# DQ-04 Duplicate Rows
# ----------------------------------------------------
def dq04_duplicate_rows(df, table):

    duplicate_rows = df.duplicated().sum()

    if duplicate_rows > 0:
        log_failure(
            "DQ-04",
            "WARNING",
            table,
            f"{duplicate_rows} duplicate rows found"
        )

# ----------------------------------------------------
# DQ-05 Positive Sales
# ----------------------------------------------------
def dq05_positive_sales(df):

    invalid = df[df["sales"] < 0]

    if not invalid.empty:
        log_failure(
            "DQ-05",
            "WARNING",
            "profitandloss",
            f"{len(invalid)} rows have negative sales."
        )


# ----------------------------------------------------
# DQ-06 Balance Sheet
# ----------------------------------------------------
def dq06_balance_sheet(df):

    invalid = df[
        df["total_assets"] < df["total_liabilities"]
    ]

    if not invalid.empty:
        log_failure(
            "DQ-06",
            "WARNING",
            "balancesheet",
            f"{len(invalid)} invalid balance sheets."
        )

# ----------------------------------------------------
# DQ-07 OPM
# ----------------------------------------------------
def dq07_opm(df):

    invalid = df[
        (df["opm_percentage"] < 0) |
        (df["opm_percentage"] > 100)
    ]

    if not invalid.empty:
        log_failure(
            "DQ-07",
            "WARNING",
            "profitandloss",
            f"{len(invalid)} invalid OPM values."
        )

# ----------------------------------------------------
# DQ-08 Future Year
# ----------------------------------------------------
def dq08_future_year(df):

    current_year = datetime.now().year

    # Convert year column to numeric
    year = pd.to_numeric(df["year"], errors="coerce")

    invalid = df[year > current_year]

    if not invalid.empty:
        log_failure(
            "DQ-08",
            "WARNING",
            "profitandloss",
            f"{len(invalid)} future years found."
        )
# ----------------------------------------------------
# DQ-09 Cash Flow
# ----------------------------------------------------
def dq09_cashflow(df):

    invalid = df[df["net_cash_flow"].isnull()]

    if not invalid.empty:
        log_failure(
            "DQ-09",
            "WARNING",
            "cashflow",
            f"{len(invalid)} missing cash flow values."
        )

# ----------------------------------------------------
# DQ-10 Stock Price
# ----------------------------------------------------
def dq10_close_price(df):

    invalid = df[df["close_price"] <= 0]

    if not invalid.empty:
        log_failure(
            "DQ-10",
            "WARNING",
            "stock_prices",
            f"{len(invalid)} invalid close prices."
        )

# ----------------------------------------------------
# DQ-11 Market Cap Validation
# ----------------------------------------------------
def dq11_market_cap(df):

    market_cap = pd.to_numeric(df["market_cap_crore"], errors="coerce")

    invalid = df[market_cap < 0]

    if not invalid.empty:
        log_failure(
            "DQ-11",
            "WARNING",
            "market_cap",
            f"{len(invalid)} negative market cap values."
        )

# ----------------------------------------------------
# DQ-12 Sector Validation
# ----------------------------------------------------
def dq12_sector(df):

    invalid = df[df["broad_sector"].isnull()]

    if not invalid.empty:
        log_failure(
            "DQ-12",
            "WARNING",
            "sectors",
            f"{len(invalid)} companies missing sector."
        )

# ----------------------------------------------------
# DQ-13 Financial Ratios
# ----------------------------------------------------
def dq13_ratios(df):

    debt = pd.to_numeric(df["debt_to_equity"], errors="coerce")

    invalid = df[debt < 0]

    if not invalid.empty:
        log_failure(
            "DQ-13",
            "WARNING",
            "financial_ratios",
            f"{len(invalid)} negative debt-to-equity ratios."
        )

# ----------------------------------------------------
# DQ-14 Annual Report
# ----------------------------------------------------
def dq14_documents(df):

    invalid = df[df["Annual_Report"].isnull()]

    if not invalid.empty:
        log_failure(
            "DQ-14",
            "WARNING",
            "documents",
            f"{len(invalid)} missing annual reports."
        )

# ----------------------------------------------------
# DQ-15 Pros and Cons
# ----------------------------------------------------
def dq15_pros_cons(df):

    invalid = df[
        df["pros"].isnull() |
        df["cons"].isnull()
    ]

    if not invalid.empty:
        log_failure(
            "DQ-15",
            "WARNING",
            "prosandcons",
            f"{len(invalid)} missing pros/cons."
        )
# ----------------------------------------------------
# DQ-16 Company Name
# ----------------------------------------------------
def dq16_company_name(df):

    invalid = df[df["company_name"].isnull()]

    if not invalid.empty:
        log_failure(
            "DQ-16",
            "CRITICAL",
            "companies",
            f"{len(invalid)} missing company names."
        )
# ----------------------------------------------------
# Validate all
# ----------------------------------------------------
def validate_all(dataframes):

    companies = dataframes["companies"]

    dq01_pk_uniqueness(companies, "id", "companies")

    dq03_missing_values(companies, "companies")

    dq04_duplicate_rows(companies, "companies")

    dq05_positive_sales(dataframes["profitandloss"])

    dq06_balance_sheet(dataframes["balancesheet"])

    dq07_opm(dataframes["profitandloss"])

    dq08_future_year(dataframes["profitandloss"])

    dq09_cashflow(dataframes["cashflow"])

    dq10_close_price(dataframes["stock_prices"])

    dq11_market_cap(dataframes["market_cap"])

    dq12_sector(dataframes["sectors"])

    dq13_ratios(dataframes["financial_ratios"])

    dq14_documents(dataframes["documents"])

    dq15_pros_cons(dataframes["prosandcons"])

    dq16_company_name(dataframes["companies"])
    # Foreign Key Checks
    dq02_fk_integrity(
        dataframes["profitandloss"],
        companies,
        "company_id",
        "id",
        "profitandloss"
    )

    dq02_fk_integrity(
        dataframes["balancesheet"],
        companies,
        "company_id",
        "id",
        "balancesheet"
    )

    dq02_fk_integrity(
        dataframes["cashflow"],
        companies,
        "company_id",
        "id",
        "cashflow"
    )

    dq02_fk_integrity(
        dataframes["analysis"],
        companies,
        "company_id",
        "id",
        "analysis"
    )

    dq02_fk_integrity(
        dataframes["financial_ratios"],
        companies,
        "company_id",
        "id",
        "financial_ratios"
    )

    dq02_fk_integrity(
        dataframes["market_cap"],
        companies,
        "company_id",
        "id",
        "market_cap"
    )

    dq02_fk_integrity(
        dataframes["stock_prices"],
        companies,
        "company_id",
        "id",
        "stock_prices"
    )

    save_failures()


if __name__ == "__main__":

    dataframes = load_all_files()

    validate_all(dataframes)

    print("Validation Completed Successfully")