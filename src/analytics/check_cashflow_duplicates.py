import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

conn.close()

print("=" * 60)
print("CASHFLOW DUPLICATE CHECK")
print("=" * 60)

print("Total cashflow rows:", len(cashflow))
print(
    "Unique companies:",
    cashflow["company_id"].nunique()
)

print(
    "Columns:",
    cashflow.columns.tolist()
)


duplicates = cashflow[
    cashflow.duplicated(
        subset=["company_id", "year"],
        keep=False
    )
].copy()


print("\nDuplicate company-year rows:")

if duplicates.empty:

    print("NONE")

else:

    print(
        duplicates[
            [
                "company_id",
                "year"
            ]
        ].sort_values(
            ["company_id", "year"]
        ).to_string(index=False)
    )

    print(
        "\nNumber of duplicate rows:",
        len(duplicates)
    )

    print(
        "Duplicate company-year combinations:",
        duplicates[
            ["company_id", "year"]
        ].drop_duplicates().shape[0]
    )