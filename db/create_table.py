import sqlite3

def create_table():
    conn = sqlite3.connect("db_agent4-1.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            base_url TEXT NOT NULL,
            spec_url TEXT NOT NULL 
        )
        """
    )

    conn.commit()

    conn.close()

create_table()
