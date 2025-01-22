#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import random
import json
from dotenv import load_dotenv
import os

load_dotenv()
api=os.getenv('SCRAPPER_API_KEY')
def scrapper_liens(query: str, max_liens: int):
    liens=[]
    payload = {'api_key': api, 'query': query, 'country_code':'fr' , 'tld':'com','num':max_liens,'time_period':'1D'}
    r = requests.get('https://api.scraperapi.com/structured/google/news', params=payload)
    response = r.text
    response_dict=json.loads(response)
    for articles in response_dict['articles']:
        liens.append(articles['link'])
    return liens

if __name__ == "__main__":
    liens = scrapper_liens("Bitcoin")
    print("Liens extraits :", liens)



