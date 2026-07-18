import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

tables = [
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

print("=" * 40)
print("ROW COUNT VERIFICATION")
print("=" * 40)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table:<20} : {count}")

conn.close()