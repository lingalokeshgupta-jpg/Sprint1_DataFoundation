import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

# Enable foreign key enforcement for this connection
cursor.execute("PRAGMA foreign_keys = ON")

# Verify it
cursor.execute("PRAGMA foreign_keys")
print("Foreign Keys:", cursor.fetchone())

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;
""")

print("\nTables:")
for table in cursor.fetchall():
    print(table[0])

# Check foreign keys for profitandloss
print("\nForeign Keys in profitandloss:")

cursor.execute("PRAGMA foreign_key_list(profitandloss)")
for row in cursor.fetchall():
    print(row)

# Close the connection LAST
conn.close()