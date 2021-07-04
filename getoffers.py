from bs4 import BeautifulSoup
from requests import get
from database import Database
from dotenv import load_dotenv
load_dotenv()
class GetOffers:
    def __init__(self, url, page, user):
        page = get(f'{url}?page={page}')
        bs = BeautifulSoup(page.content, 'html.parser')
        self.user = user
        self.bs = bs
    def get_offers(self):
        base = Database()
        tags = base.fetch_xlsx()
        iter_pages = 0
        for offer in self.bs.find_all('div', class_='offer-wrapper'):
            okTags = []
            antyTags = []
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
            iter_pages += 1
            for tag in tags[0]:
                if tag != "NaN":
                    if title.find(tag)!=-1 or title.find(tag.lower())!=-1 or title.find(tag.upper())!=-1 or title.find(tag.capitalize())!=-1 or details.find(tag)!=-1 or details.find(tag.lower())!=-1 or details.find(tag.upper())!=-1 or details.find(tag.capitalize())!=-1:
                        okTags.append(tag)
            for tag in tags[1]:
                if tag != "NaN":
                    if title.find(tag)!=-1 or title.find(tag.lower())!=-1 or title.find(tag.upper())!=-1 or title.find(tag.capitalize())!=-1 or details.find(tag)!=-1 or details.find(tag.lower())!=-1 or details.find(tag.upper())!=-1 or details.find(tag.capitalize())!=-1:
                        antyTags.append(tag)
            if not okTags:
                okTags.append('empty')
            if not antyTags:
                antyTags.append('empty')
            if okTags[0] != "empty":
                base = Database()
                if base.check_rec_not_exist(link):
                    visited = False
                    favorite = False
                    base.insert(title, link, details, okTags, antyTags, visited, favorite, self.user)
        print(iter_pages)