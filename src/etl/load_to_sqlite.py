import sqlite3
import pandas as pd
from pathlib import Path
from loader import load_all_files

DB_PATH = "db/nifty100.db"
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

TABLE_ORDER = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices"
]


def load_database():

    dataframes = load_all_files()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    audit = []

    for table in TABLE_ORDER:

        print(f"Loading {table}...")

        df = dataframes[table]

        # Replace table contents
        df.to_sql(
            table,
            conn,
            if_exists="replace",
            index=False
        )

        count = len(df)

        audit.append({
            "table": table,
            "rows_loaded": count,
            "status": "SUCCESS"
        })

        print(f"{count} rows inserted.")

    conn.commit()

    audit_df = pd.DataFrame(audit)

    audit_df.to_csv(
        OUTPUT / "load_audit.csv",
        index=False
    )

    conn.close()

    print("\nLoad Completed Successfully!")


if __name__ == "__main__":
    load_database()