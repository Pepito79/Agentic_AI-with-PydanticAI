#!/usr/bin/env python3
from dotenv import load_dotenv
import pydantic_ai
from pydantic_ai import Agent,ModelRetry, RunContext
from pydantic import BaseModel , Field
from typing import Dict, List, Optional
from pydantic_ai.models.gemini import GeminiModel
import json


load_dotenv()
modele='gemini-1.5-flash'

def Chainage_llm(input: str , List_Prompt: List[str]) -> str:
    #Etape 1 définir l'agent et l'input de l'user
    agent=Agent(modele)
    resultat_prompt_precedent = input 
    for i,Prompt_Actuel in enumerate(List_Prompt,1):
        agent= Agent(modele, system_prompt=Prompt_Actuel)
        reponse =  agent.run_sync(f"voici les données que je te donne {resultat_prompt_precedent}")
        resultat_prompt_precedent= reponse.data
        print(f"La {i} -ème étape donne: \n {resultat_prompt_precedent} ")
    return resultat_prompt_precedent
    
List_Prompt=[
    """ Transformes le texte en bullet point importants  """,
    """ Extrait tous les chiffres importants et transformes les en pourcentage
        Exemple format:
            J'ai 92 points de réussite à l'examen  --> tu dois ressortir 92%""",
    """ Traduis tout le texte en anglais""",
    """ Renvoi tout le texte en anglais les valeurs calculées dans l'ordre croissant en espagnol.
        Exemple format:
            50% , 100%  --> cien , cincuenta"""
]

Input="""Cette semaine a été pleine d'accomplissements pour moi. Tout d'abord, j'ai réussi un examen important avec un score de 92 sur 100, ce qui est bien au-dessus de la moyenne de ma classe. Cela m'a donné beaucoup de confiance pour mes futurs projets.
Ensuite, j'ai participé à une course locale qui a rassemblé 50 participants. J'ai terminé à la 2e position, ce dont je suis très fier, car je m'étais bien préparé pour cet événement sportif.
Enfin, mes efforts constants à l'école commencent à porter leurs fruits. Ma moyenne générale cette année est maintenant de 18 sur 20, ce qui montre une nette amélioration par rapport à l'année dernière.
Dans l'ensemble, je suis très satisf
ait des progrès que j'ai réalisés cette semaine et je suis déterminé à continuer sur cette lancée."""

resultat_afficher=  Chainage_llm(Input,List_Prompt)
print(resultat_afficher)

