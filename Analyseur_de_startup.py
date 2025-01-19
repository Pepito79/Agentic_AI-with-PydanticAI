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

load_dotenv()
modele='gemini-1.5-flash'

class Etapes(BaseModel):

    type: str = Field(...,description=(
        'Explique de quelle type d etape il s agit '
        'Exemple: "commerciale", "financière" , "juridique" , "logistique" ,"RH" , ...'))
    
    description: str = Field(..., description=('Décris d une manière claire et concise l etape à effectuer et comment s y prendre'))

class Reponse_Orchestrator(BaseModel):
    analyse: str = Field(..., description=(
        'Analyse et explique ce que tu as compris cette idée de startup/buisness'
        'et donne les avantages et inconvénient des approches que tu as choisies'))
    
    etapes_a_faire: List[Etapes] = Field(...,description='Liste des etapes pour lancer cette idée')

async def orchestration(idee_client: str): 
    """ Proposez diverses approches du buisness et produire les taches de chaques approches en parallel"""
    orchestrator_agent= Agent(
        model= modele,
        result_type=Reponse_Orchestrator,
        system_prompt=('Propose 2 ou 3 approches différentes pour lancer cette idée'))
    
    resultat_orchestrator= await orchestrator_agent.run(idee_client)

    analyse= resultat_orchestrator.data.analyse
    etapes= resultat_orchestrator.data.etapes_a_faire
    
    print(f'\nL analyse de votre idée est:\n{analyse}\n')
    for i in range(len(etapes)):
        print(f'La {i}-ème étape est une étape du type : {etapes[i].type}')
        print(f'Sa description est la suivante:\n{etapes[i].description}\n \n')


    worker_agent=Agent(
        model=modele,
        system_prompt=('Propose un petit plan d action pour réaliser la description de l etape et n utilise surtout pas le caractère * dans ton texte ',
         ' a la place met des esapces si il le faut ',
         'et dès que tu finis un plan met une ligne de tiret (ex: ----------------) de la longeur de la ligne pour séparer les blocs')
    )
    worker_reponse= await asyncio.gather(*[
        worker_agent.run(json.dumps(
            {'Idée du client': idee_client } | etapes_info.model_dump() 
        )) for etapes_info in etapes
    ])

    for etape, rep in zip(etapes,worker_reponse):
        print(f'Pour l etape du type {etape.type}\nOn propose:\n{rep.data}')
    
async def main():
    parser = argparse.ArgumentParser(description="Lancez une orchestration pour créer une startup.")
    parser.add_argument('description', nargs='?', type=str, help="Description de l'idée de startup")
    
    args = parser.parse_args()
    
    if not args.description:
        # Si aucun argument n'est passé, demander à l'utilisateur de saisir son idée
        args.description = input("Veuillez saisir votre idée pour la startup : ")
    
    await orchestration(args.description)

if __name__ == "__main__":
    asyncio.run(main())