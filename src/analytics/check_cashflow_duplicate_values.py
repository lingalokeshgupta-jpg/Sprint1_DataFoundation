import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

conn.close()


duplicates = cashflow[
    cashflow.duplicated(
        subset=["company_id", "year"],
        keep=False
    )
].copy()


duplicates = duplicates.sort_values(
    ["company_id", "year"]
)


print("=" * 70)
print("CASHFLOW DUPLICATE VALUE CHECK")
print("=" * 70)


for (company, year), group in duplicates.groupby(
    ["company_id", "year"]
):

    print("\n----------------------------------------")
    print("Company:", company)
    print("Year:", year)

    print(
        group[
            [
                "id",
                "company_id",
                "year",
                "operating_activity",
                "investing_activity",
                "financing_activity",
                "net_cash_flow"
            ]
        ].to_string(index=False)
    )

    values = group[
        [
            "operating_activity",
            "investing_activity",
            "financing_activity",
            "net_cash_flow"
        ]
    ].drop_duplicates()

    if len(values) == 1:
        print("STATUS: IDENTICAL DUPLICATES")
    else:
        print("STATUS: DIFFERENT FINANCIAL VALUES")