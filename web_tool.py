#!/usr/bin/env python3
from dotenv import load_dotenv
import pydantic_ai
from pydantic_ai import Agent,ModelRetry, RunContext
from pydantic import BaseModel,Field
from typing import Dict, List, Optional
from pydantic_ai.models.gemini import GeminiModel
import json
import asyncio
import argparse
from bs4 import BeautifulSoup , Comment
import requests
from markdownify import markdownify as md

load_dotenv()
modele='gemini-1.5-flash'


liens=['https://kylianmbappe.com/', 'https://en.wikipedia.org/wiki/Kylian_Mbapp%C3%A9', 'https://www.transfermarkt.com/kylian-mbappe/profil/spieler/342229', 'https://www.britannica.com/biography/Kylian-Mbappe', 'https://www.espn.com/soccer/player/_/id/231388/kylian-mbappe', 'https://www.si.com/onsi/soccer/real-madrid/kylian-mbappe-profile', 'https://simple.wikipedia.org/wiki/Kylian_Mbapp%C3%A9', 'https://www.transfermarkt.com/kylian-mbappe/leistungsdaten/spieler/342229', 'https://www.realmadrid.com/en-US/football/first-team/players/kylian-mbappe', 'https://www.cnn.com/2024/06/03/sport/kylian-mbappe-real-madrid-psg-spt-intl/index.html', 'https://fbref.com/en/players/42fd9c7f/Kylian-Mbappe', 'https://kylianmbappe.com/', 'https://en.wikipedia.org/wiki/Kylian_Mbapp%C3%A9', 'https://www.transfermarkt.com/kylian-mbappe/profil/spieler/342229', 'https://www.espn.com/soccer/player/_/id/231388/kylian-mbappe', 'https://www.cnn.com/2024/06/03/sport/kylian-mbappe-real-madrid-psg-spt-intl/index.html', 'https://www.cnn.com/2022/12/18/football/kylian-mbappe-best-player-qatar-2022-messi-spt-intl/index.html', 'https://www.si.com/onsi/soccer/real-madrid/matchday/real-madrid-4-1-las-palmas-player-ratings-as-kylian-mbappe-shines-in-la-liga-win', 'https://www.transfermarkt.com/kylian-mbappe/leistungsdaten/spieler/342229', 'https://apnews.com/article/kylian-mbappe-psg-30c3d6d71393f2f5fad5a5ad0c10af52', 'https://www.cnn.com/2024/03/06/sport/kylian-mbappe-psg-real-sociedad-champions-league-spt-intl/index.html', 'https://en.psg.fr/teams/first-team/squad/kylian-mbappe']

class Review_KM(BaseModel):
    pos_titre: int = Field(...,description='Le nombre de mots positifs dans le titre de l article')
    neg_titre: int = Field(..., description='Le nombre de mots négatifs dans le titre de l article') 
    titre_pos: bool = Field(..., description ='Est ce que le titre stipule quelque chose de positif sur Mbappé?')
    resume: str = Field(..., description='Un résumé general de l article sur Mbappé (neutre,positif,excellent,médiocre ...)')
    note: float = Field(...,description=(
        'Une note sur la positivité de l article '
        'plus l article est positif plus la note se raproche de 20')
    )
    positif: int = Field(..., description='Le nombre de mots positifs sur Kylian Mbappé')
    negatifs: int= Field(...,description='Le nombre de mots négatifs sur Kylian Mbappé')
    source: str = Field(...,description='Nom de la presse qui a écrit l article')
    forme_actuelle: str = Field(...,description='Etat de forme actuel de Kylian Mbappé')



kylian_Agent= Agent(
    modele,
    result_type= Review_KM,
    system_prompt='Tu et un analyste sportif tu doit anaylser mbappé en fonction des infos de l url'
)

@kylian_Agent.tool_plain
async def scrapper(url : str) -> str|None:
    """Un lien est donné en arg le but est de scrappe les données du lien et en extraire le texte """
    response = requests.get(url)
    soup= BeautifulSoup(response.text,'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    final= soup.prettify()
    return md(final)

async def main():
    for i in range (len(liens)):
        resultat= await kylian_Agent.run(liens[i])
        print((resultat.data.model_dump()))

if __name__ == "__main__":
    asyncio.run(main())
