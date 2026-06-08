import sqlite3
from pathlib import Path


class AgentDatabase:

    def __init__(self, database_path):
        self.database_path = database_path
                
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.database_path)
            self.conn.row_factory = sqlite3.Row
            print("[AgentDatabase] Successfully connected to database.")
        except Exception as e:
            print(f"[AgentDatabase]: ERROR in connect: {e}")

    def select(self, query: str):
        cursor = self.conn.cursor()

        cursor.execute(query)
        return cursor.fetchall()


    def disconnect(self):
        try:
            self.conn.close()
            print("[AgentDatabase] Succesfully disconnected from database.")
        except Exception as e:
            print(f"[AgentDatabase]: ERROR in disconnect: {e}")