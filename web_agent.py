#!/usr/bin/env python3
from dotenv import load_dotenv
import pydantic_ai
from pydantic_ai import Agent,ModelRetry, RunContext
from pydantic import BaseModel,Field
from typing import Dict, List, Optional
from pydantic_ai.models.gemini import GeminiModel
from bs4 import BeautifulSoup,Comment
import json
import asyncio
import requests
import os
from markdownify import markdownify as md


load_dotenv()
api=os.getenv('SCRAPPER_API_KEY')
modele='gemini-1.5-flash'




class Resultat_Web(BaseModel):
    resume: List[str] = Field(...,description='Résume chaque lien que tu lis')
    nombre_liens: int = Field(...,description='Le nombre de liens que tu as visités')
    final_resume: str = Field(...,description='Résumé de tous les liens que tu as visités')

web_agent=Agent(
    modele,
    result_type=Resultat_Web,
    system_prompt=(
        'effectue une recherche sur ce qui est demandé  et il faut que {max_liens} soit au moins égal à 4 ',
        'il faudra que tu utilises l outil {scrappe_liens} pour prendre les liens en relations  avec le sujet','qui est {query}'
        'puis tu visiteras lien par lien avec l outil {visiter_lien}',' Ne depasse jamais 15 pour {max_liens}',
    )
)

@web_agent.tool_plain
def visiter_lien(lien: str):
    """Un lien est donné en arg le but est de scrappe les données du lien et en extraire le texte """
    response = requests.get(lien)
    soup= BeautifulSoup(response.text,'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    final= soup.prettify()
    return md(final)

@web_agent.tool_plain
def scrapper_liens(query: str, max_liens: int):
    """ query correspond a la recherhce à effectuer et max_liens le maximum de liens a cherches"""
    liens=[]
    payload = {'api_key': api, 'query': query, 'country_code':'fr' , 'tld':'com','num':max_liens,'time_period':'1D'}
    r = requests.get('https://api.scraperapi.com/structured/google/news', params=payload)
    response = r.text
    response_dict=json.loads(response)
    for articles in response_dict['articles']:
        liens.append(articles['link'])
    return liens

def main(sujet:str):
    resultat= web_agent.run_sync(sujet).data
    res_dict=resultat.model_dump()
    for key in res_dict:
        print(f'{key} : {res_dict[key]} \n')

if __name__ == "__main__":
    main("Je recherche des infos sur les méthodes stochastiques en finances")
