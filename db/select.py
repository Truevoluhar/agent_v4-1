import sqlite3

conn = sqlite3.connect("db_agent4-1.db")
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute("SELECT * FROM services")
rows = cursor.fetchall()

for row in rows:
    print(row["service_name"])

conn.close()