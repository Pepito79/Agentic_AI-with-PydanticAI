#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import random

def scrapper():
   

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    liens = []
    for i in range(5):
         
         url_base = "https://html.duckduckgo.com/html/?q=kylian+mbappe&s={}"
         url=url_base.format(i*10)
         response = requests.get(url, headers=headers, allow_redirects=True)
         print("Status code:", response.status_code)
         if response.status_code != 200:
              print("Erreur d'accès au serveur")
         else:
            soup = BeautifulSoup(response.text, 'html.parser')
            resultats = soup.find_all('a', {'class': 'result__a'})
            for resultat in resultats:
                link = resultat.get('href')
                liens.append(link)
    time.sleep(random.uniform(2, 4))

    return liens



if __name__ == "__main__":
    print(scrapper())
