import sqlite3

class Database:
    def __init__(self,  name):
        self.db = sqlite3.connect(name)
        self.cursor = self.db.cursor()

    def __del__ (self):
        self.db.close()

    def create_db(self, sql: str):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            print('table exists')

    def insert(self, *values):
        self.cursor.execute(f"INSERT INTO offers VALUES ({','.join(['?' for _ in values])})", values)
        self.db.commit()

    def insert_xlsx(self, *values):
        self.cursor.execute(f"INSERT INTO xlsx VALUES ({','.join(['?' for _ in values])})", values)
        self.db.commit()

    def fetch_link(self, **conditions):
        values = list(conditions.values())[0]
        result = self.cursor.execute('''SELECT * FROM offers WHERE title LIKE ?''', [f"%{values}%"])
        self.db.commit()
        return result
        #return self.cursor.execute(f"SELECT * FROM offers WHERE title LIKE '%{values}%'")

    def fetch_search(self):
        xlsxPhrases = self.cursor.execute('''SELECT phrase FROM xlsx''').fetchall()
        listResult = [x[0] for x in xlsxPhrases]
        listResult = ['%'+s+'%' for s in listResult]
        result = self.cursor.execute(f"SELECT * FROM offers WHERE details LIKE {' OR title LIKE '.join(['?' for _ in listResult])}", listResult)
        self.db.commit()
        return list(result)