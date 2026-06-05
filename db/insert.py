import sqlite3


SQL = """
INSERT INTO SERVICES (service_name, base_url, spec_url) VALUES (?, ?, ?)
"""



def insert():
    conn = sqlite3.connect("db_agent4-1.db")
    cursor = conn.cursor()

    cursor.execute(SQL, ("AUTH_SERVICE", "http://localhost:8001/", "http://localhost:8001/openapi.json"))

    conn.commit()

    cursor.execute("SELECT * FROM services")
    print(cursor.fetchall())
    conn.close()

insert()