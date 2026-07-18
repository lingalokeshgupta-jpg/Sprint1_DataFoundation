import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

with open("db/schema.sql", "r", encoding="utf-8") as f:
    sql = f.read()

cursor.executescript(sql)

conn.commit()

conn.close()

print("Database created successfully!")