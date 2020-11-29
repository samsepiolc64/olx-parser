from bs4 import BeautifulSoup
from requests import get
from database import Database
from dotenv import load_dotenv
load_dotenv()

class GetOffers:
    def __init__(self, url, page):
        page = get(f'{url}?page={page}')
        bs = BeautifulSoup(page.content, 'html.parser')
        self.bs = bs

    def get_offers(self):
        base = Database()
        tags = base.fetch_xlsx()
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
            tagFlag = False
            for tag in tags[0]:
                if details.find(tag) > 0 or title.find(tag) > 0:
                    tagFlag = True
                    okTags.append(tag)
            antyTagFlag = False
            for tag in tags[1]:
                if details.find(tag) > 0 or title.find(tag) > 0:
                    antyTagFlag = True
                    antyTags.append(tag)
            if not okTags:
                okTagsFlag = False
                okTags.append('empty')
            if not antyTags:
                antyTagsFlag = False
                antyTags.append('empty')
            if tagFlag or antyTagFlag and (okTagsFlag and antyTagsFlag):
                base = Database()
                base.insert(title, link, details, okTags, antyTags)