import sqlite3
import pandas as pd

# Read your cleaned cashflow CSV
df = pd.read_csv("data/processed/05_cashflow_clean.csv")   # <-- replace with your actual filename

# Keep only ATGL rows
atgl = df[df["company_id"] == "ATGL"]

conn = sqlite3.connect("db/nifty100.db")

# Append to the existing table
atgl.to_sql(
    "cashflow",
    conn,
    if_exists="append",
    index=False
)

conn.close()

print("Inserted", len(atgl), "ATGL rows.")