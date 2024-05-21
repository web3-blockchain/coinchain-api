from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

class Config:
    COOKIE = os.getenv('COOKIE')
    NEWS_URL = 'https://coinmarketcap.com/headlines/news/'
    NEWS_CONTAINER_CLASS = 'infinite-scroll-component'
    NEWS_ITEM_CLASS = 'sc-aef7b723-0 sc-b1d35755-0 cGYUCj'
    LINK_CONTAINER_CLASS = 'sc-aef7b723-0 coCmGz'
