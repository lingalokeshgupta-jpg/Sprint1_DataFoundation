import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("PRAGMA foreign_key_check")

errors = cursor.fetchall()

if len(errors) == 0:
    print("✅ Foreign Key Check Passed (0 violations)")
else:
    print("❌ Foreign Key Violations Found:")
    for error in errors:
        print(error)

conn.close()