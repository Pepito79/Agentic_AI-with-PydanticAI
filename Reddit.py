#!/usr/bin/env python3
from dotenv import load_dotenv
import pydantic_ai
from pydantic_ai import Agent
from pydantic import BaseModel,Field
from typing import Dict, List, Optional
from pydantic_ai.models.gemini import GeminiModel
from bs4 import BeautifulSoup,Comment
import json
import requests
from markdownify import markdownify as md


load_dotenv()
modele='gemini-1.5-flash'

class Resultat_Web(BaseModel):
    resume: str = Field(...,description='Résume d une manière concisen et générale les messages de la page et leur contenu')
    langue: str = Field(...,description= 'Langue orignale du post Reddit ')
    reponse: str = Field(...,description='Une réponse au Reddit qui sera publié sur ce reddit et  ne dépassant pas les 3 lignes et dans la langue du Reddit ')

#L'agent web qui va effectuer des recherches sur la crypto en question 
web_agent=Agent(
    modele,
    result_type=Resultat_Web,
        system_prompt=(
        'Tu es un agent dont le but est de générer des réponses en relation avec un thème Reddit. '
        'Analyse les réponses du lien Reddit qui te sera donné et génère une réponse adaptée au thème et aux commentaires. '
        'Évite les réponses du type : "oui c est bien", "oui c est cool", "intéressant". '
        'Cette réponse a pour but d\'être publiée sur le Reddit en question. '
        'Il faut des réponses précises et de taille moyenne, comme si c\'était un humain qui l\'avait écrite, avec un langage normal pas soutenu. '
        'Voici quelques exemples de réponses adaptées : '
        '- "Je pense que cette approche est intéressante, mais il faut aussi considérer les risques liés à la volatilité du marché." '
        '- "As-tu envisagé d\'utiliser une autre plateforme pour réduire les frais de transaction ?" '
        '- "Je suis d\'accord avec ton point de vue, mais il serait utile d\'ajouter plus de données pour étayer ton argument."'
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

def nettoyer_reponse(reponse: str) -> str:
    """
    Nettoie la réponse pour supprimer les phrases descriptives du post.
    """
    phrases_interdites = [
        "The post highlights",
        "Le post parle de",
        "Le post explique",
        "The post discusses",
        "This post is about",
    ]
    for phrase in phrases_interdites:
        if reponse.startswith(phrase):
            reponse = reponse[len(phrase):].strip()
            reponse = reponse[0].upper() + reponse[1:]  
    return reponse

def main():
    sujet = input ("> À quel lien Reddit veux tu générer un réponse : ")
    resultat= web_agent.run_sync(sujet).data
    res_dict=resultat.model_dump()
    res_dict['reponse'] = nettoyer_reponse(res_dict['reponse'])
    for key in res_dict:
        print(f'{key} : {res_dict[key]} \n')

if __name__ == "__main__":
    main()
