import psycopg2
from os import getenv

class Database:
    def __init__(self):
        self.db = psycopg2.connect(dbname=getenv('DB_NAME'), port=getenv('DB_PORT'), user=getenv('DB_USER'), password=getenv('DB_PASS'), host=getenv('DB_HOST'))
        self.cursor = self.db.cursor()

    def __del__ (self):
        self.db.close()

    def create_db(self, sql: str):
        self.cursor.execute(sql)
        self.db.commit()

    def settings_init(self, *values):
        for value in values:
            print(value.split(":"))
            self.cursor.execute(f"INSERT INTO settings (setting, value) VALUES (%s, %s)", value.split(":"))
        self.db.commit()

    def fetch_settings(self):
        try:
            phraseCursor = self.db.cursor()
            phraseCursor.execute("SELECT * FROM settings")
            result = phraseCursor.fetchall()
            self.db.commit()
            return list(result)
        except:
            return "error"

    def save_settings(self, values):
        for value in values:
            self.cursor.execute(f"UPDATE settings SET value = {str(values[value][0])} WHERE id = {int(value)}")
        self.db.commit()

    def insert(self, *values):
        self.cursor.execute("""INSERT INTO offers (title, link, details, oktags, antytags, visited, favorite) VALUES (%s, %s, %s, ARRAY [%s], ARRAY [%s], %s, %s)""", values)
        self.db.commit()

    def insert_xlsx(self, *values):
        self.cursor.execute("""INSERT INTO xlsx (phrase, antyphrase) VALUES (%s,%s)""", values)
        self.db.commit()

    def fetch_tags(self):
        xlsxCursor = self.db.cursor()
        xlsxCursor.execute("SELECT phrase, antyphrase FROM xlsx")
        xlsxPhrases = xlsxCursor.fetchall()
        phrases = [x[0] for x in xlsxPhrases]
        antyPhrases = [x[1] for x in xlsxPhrases]
        self.db.commit()
        return [list(phrases), list(antyPhrases)]

    # def fetch_searchold(self):
    #     try:
    #         xlsxCursor = self.db.cursor()
    #         xlsxCursor.execute("SELECT phrase FROM xlsx")
    #         xlsxPhrases = xlsxCursor.fetchall()
    #         listResult = [x[0] for x in xlsxPhrases]
    #         listResult = ['%'+s+'%' for s in listResult]
    #         phraseCursor = self.db.cursor()
    #         phraseCursor.execute(f"SELECT * FROM offers WHERE details LIKE {' OR details LIKE '.join(['%s' for _ in listResult])}", listResult)
    #         result = phraseCursor.fetchall()
    #         self.db.commit()
    #         return list(result)
    #     except:
    #         return []

    def fetch_search(self):
        try:
            phraseCursor = self.db.cursor()
            phraseCursor.execute("SELECT * FROM offers")
            result = phraseCursor.fetchall()
            self.db.commit()
            return list(result)
        except:
            return "error"

    def fetch_xlsx(self):
        try:
            xlsxCursor = self.db.cursor()
            xlsxCursor.execute("SELECT phrase, antyphrase FROM xlsx")
            xlsxPhrases = xlsxCursor.fetchall()
            phrases = [x[0] for x in xlsxPhrases]
            antyPhrases = [x[1] for x in xlsxPhrases]
            self.db.commit()
            return [list(phrases), list(antyPhrases)]
        except:
            return "error"

    def check_rec_not_exist(self, *link):
        linkCursor = self.db.cursor()
        linkCursor.execute("SELECT COUNT(link) FROM offers WHERE link = %s", link)
        result = linkCursor.fetchall()
        self.db.commit()
        if result[0][0] == 0:
            return True



    def count_row_offers(self):
        try:
            countCursor = self.db.cursor()
            countCursor.execute("SELECT count(*) FROM offers")
            result = countCursor.fetchone()
            self.db.commit()
            return result
        except:
            return "error"
