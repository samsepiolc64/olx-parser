import psycopg2
from os import getenv


class Database:
    def __init__(self):
        self.db = psycopg2.connect(dbname=getenv('DB_NAME'), port=getenv('DB_PORT'), user=getenv('DB_USER'), password=getenv('DB_PASS'), host=getenv('DB_HOST'))
        self.cursor = self.db.cursor()

    def __del__ (self):
        self.db.close()

    def create_db(self, sql: str):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            return "table exists"


    def insert(self, *values):
        self.cursor.execute("""INSERT INTO offers (title, link, details) VALUES (%s, %s, %s)""", values)
        self.db.commit()

    def insert_xlsx(self, *values):
        self.cursor.execute("""INSERT INTO xlsx (phrase) VALUES (%s)""", values)
        self.db.commit()

    def fetch_link(self, **conditions):
        values = list(conditions.values())[0]
        result = self.cursor.execute('''SELECT link FROM offers WHERE title LIKE ?''', [f"%{values}%"])
        self.db.commit()
        return result

    def fetch_search(self):
        try:
            xlsxCursor = self.db.cursor()
            xlsxCursor.execute("SELECT phrase FROM xlsx")
            xlsxPhrases = xlsxCursor.fetchall()
            listResult = [x[0] for x in xlsxPhrases]
            listResult = ['%'+s+'%' for s in listResult]
            phraseCursor = self.db.cursor()
            phraseCursor.execute(f"SELECT * FROM offers WHERE details LIKE {' OR title LIKE '.join(['%s' for _ in listResult])}", listResult)
            result = phraseCursor.fetchall()
            self.db.commit()
            return list(result)
        except:
            return []