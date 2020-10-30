import sqlite3

class Database:
    def __init__(self,  name):
        self.db = sqlite3.connect(name)
        self.cursor = self.db.cursor()

    def __del__ (self):
        self.db.close()

    def create_db(self, sql: str):
        self.cursor.execute(sql)
        self.db.commit()

    def insert(self, *values):
        self.cursor.execute(f"INSERT INTO offers VALUES ({','.join(['?' for _ in values])})", values)
        self.db.commit()

    def fetch_link(self, **conditions):
        values = conditions.values()
        return self.cursor.execute(f"SELECT * FROM offers WHERE {'and'.join([f'{condition}=?' for condition in conditions])}", list(values))