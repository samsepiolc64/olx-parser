import psycopg2
import pandas as pd
import os
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

    # ***********************************
    # ***          settings           ***
    # ***********************************

    def settings_init(self, *values):
        for value in values:
            print(value.split(":"))
            self.cursor.execute(f"INSERT INTO settings (setting, value) VALUES (%s, %s)", value.split(":"))
        self.db.commit()

    def fetch_settings(self):
        try:
            phraseCursor = self.db.cursor()
            phraseCursor.execute("SELECT * FROM settings ORDER BY id ASC")
            result = phraseCursor.fetchall()
            self.db.commit()
            return list(result)
        except:
            return "error"

    def save_settings(self, values):
        for value in values:
            if values[value][0] == "on" or values[value][0] == "True":
                tmpvalue = True
            else:
                tmpvalue = str(values[value][0])
            self.cursor.execute(f"UPDATE settings SET value = {tmpvalue} WHERE id = {int(value)}")
        self.db.commit()

    # ***********************************
    # ***            offers           ***
    # ***********************************

    def insert(self, *values):
        self.cursor.execute("""INSERT INTO offers (title, link, details, oktags, antytags, visited, favorite) VALUES (%s, %s, %s, ARRAY [%s], ARRAY [%s], %s, %s)""", values)
        self.db.commit()

    def fetch_search(self, filtr):
        try:
            phraseCursor = self.db.cursor()
            if filtr == 0:
                phraseCursor.execute("SELECT * FROM offers ORDER BY id DESC")
            if filtr == 1:
                phraseCursor.execute("SELECT * FROM offers WHERE favorite = true ORDER BY id DESC")
            if filtr == 2:
                phraseCursor.execute("SELECT * FROM offers WHERE visited = true ORDER BY id DESC")
            if filtr == 3:
                phraseCursor.execute("SELECT * FROM offers WHERE favorite = true AND visited = true ORDER BY id DESC")
            if filtr == 4:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] = 'empty' ORDER BY id DESC")
            if filtr == 5:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] = 'empty' AND favorite = true ORDER BY id DESC")
            if filtr == 6:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] = 'empty' AND visited = true ORDER BY id DESC")
            if filtr == 7:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] = 'empty' AND favorite = true AND visited = true ORDER BY id DESC")
            if filtr == 8:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] != 'empty' ORDER BY id DESC")
            if filtr == 9:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] != 'empty' AND favorite = true ORDER BY id DESC")
            if filtr == 10:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] != 'empty' AND visited = true ORDER BY id DESC")
            if filtr == 11:
                phraseCursor.execute("SELECT * FROM offers WHERE antytags[1][1] != 'empty' AND favorite = true AND visited = true ORDER BY id DESC")

            result = phraseCursor.fetchall()
            self.db.commit()
            return list(result)
        except:
            return "error"


    def fetch_search_xxx(self):
        try:
            phraseCursor = self.db.cursor()
            phraseCursor.execute("SELECT * FROM offers ORDER BY id DESC")
            result = phraseCursor.fetchall()
            self.db.commit()
            return list(result)
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

    def save_offer(self, values):
        keys = []
        for value in values:
            keys.append(value)
        if len(keys) > 1:
            for key in range(len(keys)):
                id_elem = keys[0]
                if key > 0:
                    column = keys[key]
                    if column == "deleted":
                        self.cursor.execute(f"DELETE FROM offers WHERE id = {int(id_elem)}")
                    elif (values[column][0] == "on") or (values[column][0] == "True"):
                        self.cursor.execute(f"UPDATE offers SET {column} = True WHERE id = {int(id_elem)}")
                    else:
                        self.cursor.execute(f"UPDATE offers SET {column} = False WHERE id = {int(id_elem)}")
        self.db.commit()

    # ***********************************
    # ***             xlsx            ***
    # ***********************************
    def base_to_xlsx(self):
        def make_hyperlink(value):
            return '=HYPERLINK("%s")' % value

        xlsx = pd.read_sql(sql="SELECT title, link FROM offers", con=self.db)
        # xlsx['link'] = xlsx['link'].apply(lambda x: make_hyperlink(x))
        # xlsx.to_excel("excel-test.xlsx")
        # xlsx.to_html("excel-test.html")
        # webbrowser.open("excel-test.html")
        # return("ok")
        data = xlsx.to_csv()
        # data = xlsx.to_excel()
        return data

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