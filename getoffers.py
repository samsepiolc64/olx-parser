from bs4 import BeautifulSoup
from requests import get
from database import Database
from os import getenv
from dotenv import load_dotenv
load_dotenv()

class GetOffers:
    def __init__(self, url, page):
        page = get(f'{url}?page={page}')
        bs = BeautifulSoup(page.content, 'html.parser')
        self.bs = bs

    def get_offers(self):
        for offer in self.bs.find_all('div', class_='offer-wrapper'):
            offer_content = offer.find('td', class_='title-cell')
            title = offer_content.find('strong').get_text().strip()
            link = offer_content.find('a', class_='link')['href']
            subpage = get(link)
            sub_bs = BeautifulSoup(subpage.content, 'html.parser')
            sub_offer = sub_bs.find('div', class_='descriptioncontent')
            try:
                details = sub_offer.find(id='textContent').get_text().strip()
            except:
                details = "no details"
            base = Database(getenv('DB_NAME'))
            base.insert(None, title, link, details)