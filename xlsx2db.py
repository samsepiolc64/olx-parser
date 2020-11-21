from bs4 import BeautifulSoup
from requests import get
from database import Database
from os import getenv
from dotenv import load_dotenv
load_dotenv()

class Xlsx2Db:
    def __init__(self):
        pass

    def xlsx2db(self, data):
        for i in data:
            base = Database()
            base.insert_xlsx(i[0])