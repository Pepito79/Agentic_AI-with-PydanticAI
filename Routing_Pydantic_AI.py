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

class Choix_Agent_Maitre(BaseModel):
    Choix: str = Field(..., description="Le nom de la route choisie (i.e agent utilisé)")
    Explication: str 
    Contexte: str = Field(...,description='Réexplique le contexte avec tous les détails nécessaire sans ajouter de données de chez toi')
    Ressenti : str = Field(...,description='Analyse la réponse de lutilisateur et analyse le sentiment global ressenti')

class Reponse_Team(BaseModel):
    Reponse: str 
    Etat_Critique: bool
    Appel_Humain: bool = Field(...,description='Tu dois spécifier si cette requête nécessite de faire appel à un humain ou pas')

def route(Team_Agent: Dict[str,str] , Ticket: str):
    agent_maitre = Agent(
        modele,
        result_type=Choix_Agent_Maitre,
        system_prompt= ('Analyse le ticket/requete du client et choisi quel,',
                        'agent de la team appeler sachant que la liste disponnible des agents',
                        f'est la suivante : {Team_Agent.keys()} ', 
                        f'et que chaque agent fait la tache suivante {Team_Agent.values()}' 
    )
    )  

    reponse_maitre= agent_maitre.run_sync(Ticket)
    Choix_agent= reponse_maitre.data.Choix.strip('"')
    Explication = reponse_maitre.data.Explication
    Ressenti_User= reponse_maitre.data.Ressenti

    print(f'Le nom de la team appelée est: {Choix_agent} \n ')
    print(f'Cela est expliqué par :\n{Explication} \n')

    Appel_travailleur= Agent(modele,result_type=Reponse_Team,system_prompt=Team_Agent[Choix_agent])
    reponse_finale=Appel_travailleur.run_sync(Ticket).data
    print(f'Etat critique ? : {reponse_finale.Etat_Critique} \n')
    print(f'Faire appel à un agent humain : {reponse_finale.Appel_Humain} \n')

    return(reponse_finale.Reponse)
    


agents = {
    "Équipe Commerciale": """Responsabilités :
- Identifier et contacter des entreprises du BTP susceptibles d'acheter du fer
- Négocier les prix et les conditions de vente
- Élaborer des propositions commerciales personnalisées
- Analyser le marché et la concurrence

Objectifs :
- Augmenter le nombre de clients dans le secteur du BTP
- Optimiser les marges de vente

Guide :
1. Commencez par saluer le client et comprendre ses besoins spécifiques.
2. Proposez des solutions adaptées aux besoins du client, en mettant l'accent sur la qualité et la durabilité du fer vendu.
3. Expliquez les conditions de vente et le processus de commande.
4. Fournissez un devis clair et détaillé.
5. Assurez-vous que le client comprend toutes les étapes avant la livraison et la facturation.

Modèle :
Bonjour [Nom du client],  
Merci de nous avoir contactés concernant vos besoins en fer. Nous avons bien pris en compte vos spécifications.  
Nous vous proposons [solution adaptée], qui offre une excellente durabilité et qualité pour vos projets.  
Voici un devis détaillé : [détails du devis].  
Si vous avez des questions ou souhaitez confirmer cette commande, n'hésitez pas à nous contacter.  
Cordialement,  
[Votre nom]  
Spécialiste Commercial""",

    "Équipe Logistique": """Responsabilités :
- Planifier les livraisons de fer aux clients
- Gérer les stocks et les réapprovisionnements
- Suivre les commandes et les retours
- Veiller à la conformité des livraisons avec les normes du secteur

Objectifs :
- Assurer une livraison dans les délais impartis
- Réduire les erreurs de livraison et les retours

Guide :
1. Commencez par vérifier la commande et les détails de livraison.
2. Coordonnez avec les transporteurs pour garantir une livraison efficace et à temps.
3. Vérifiez l'état du stock et anticipez les besoins futurs.
4. Fournissez des mises à jour régulières aux équipes commerciales et aux clients.
5. Assurez-vous que la livraison respecte les normes de sécurité et de qualité.

Modèle :
Bonjour [Nom du client],  
Votre commande n°[numéro de commande] est en cours de traitement. Elle sera expédiée le [date prévue de livraison].  
Nous avons vérifié les stocks et confirmé la disponibilité des produits.  
Pour toute mise à jour ou changement, veuillez nous contacter rapidement.  
Cordialement,  
[Votre nom]  
Spécialiste Logistique""",

    "Équipe Technique": """Responsabilités :
- Assurer la qualité et la conformité du fer vendu
- Fournir des conseils techniques aux clients sur l'utilisation du fer
- Analyser les retours clients concernant la qualité des produits
- Développer des solutions techniques pour améliorer l'offre de fer

Objectifs :
- Optimiser la qualité du produit
- Réduire les plaintes liées aux défauts de produit

Guide :
1. Commencez par analyser la situation et collecter des informations détaillées sur le problème technique.
2. Vérifiez la qualité du fer vendu selon les spécifications.
3. Fournissez des solutions concrètes ou des ajustements possibles au produit.
4. Si nécessaire, guidez le client à travers des tests ou des vérifications supplémentaires.
5. En cas de besoin, escaladez le problème à un responsable qualité.

Modèle :
Bonjour [Nom du client],  
Nous avons bien reçu votre demande concernant [problème technique]. Après analyse, voici nos recommandations :  
1. [Étape 1 pour résoudre le problème]  
2. [Étape 2, vérification ou ajustement].  
Nous restons à votre disposition pour toute assistance supplémentaire ou vérification sur place.  
Cordialement,  
[Votre nom]  
Spécialiste Technique""",

    "Équipe Comptabilité": """Responsabilités :
- Gérer les factures et les paiements
- Vérifier les paiements en attente et traiter les relances
- Équilibrer les comptes de l'entreprise
- Assurer la conformité fiscale et comptable

Objectifs :
- Réduire les délais de paiement des clients
- Maintenir des comptes précis et à jour

Guide :
1. Commencez par examiner les détails de la facture et confirmer le montant à payer.
2. Si une question est soulevée, expliquez clairement les frais ou les écarts.
3. Décrivez les étapes pour résoudre le problème ou clarifier la situation.
4. Proposez des solutions de paiement adaptées si nécessaire.
5. Si le problème persiste, dirigez le client vers l'équipe concernée pour une résolution rapide.

Modèle :
Bonjour [Nom du client],  
Nous avons constaté un paiement en attente pour la facture n°[numéro de facture], d'un montant de [montant].  
Pour régulariser la situation, veuillez effectuer le paiement avant le [date limite].  
Si vous avez des questions concernant cette facture, nous sommes disponibles pour vous aider.  
Cordialement,  
[Votre nom]  
Spécialiste Comptabilité"""
}


tickets = [
    """Subject: Demande d'informations sur les offres commerciales
    Message: Bonjour,

Je suis intéressé par l'achat de fer pour un projet de construction, mais j'aimerais obtenir plus de détails sur vos offres et conditions de vente. Pourriez-vous me fournir un devis personnalisé en fonction de nos besoins en matériaux et du délai de livraison ? Nous avons un chantier qui démarre dans les prochaines semaines, donc ce serait utile de connaître les options disponibles.

Merci de votre réactivité.

Cordialement,  
- Marie Dupont, Directrice des achats, Construction MétalPro""",

    """Subject: Demande de suivi de livraison
    Message: Bonjour,

Je voudrais savoir où en est la livraison de notre commande de fer, prévue pour le chantier situé à 125 Rue du Bâtiment, Paris. La date de livraison approche et nous n'avons pas encore reçu de confirmation. Pourriez-vous me donner un point sur la situation de cette livraison et m'informer des étapes suivantes ?

Merci beaucoup pour votre aide.

Cordialement,  
- Thomas Leroy, Responsable Logistique, BTP Durables""",

    """Subject: Problème de qualité du fer livré
    Message: Bonjour,

Nous avons reçu notre commande de fer, mais après inspection, nous avons constaté que certains morceaux présentent des défauts de qualité. Pourriez-vous nous conseiller sur les étapes à suivre pour procéder à un retour ou à un remplacement des pièces concernées ? Nous avons besoin de garantir la sécurité et la solidité des matériaux pour notre chantier.

Merci pour votre aide.

Cordialement,  
- Laura Martin, Chef de projet, Construction MétalPro""",

    """Subject: Question sur la facturation
    Message: Bonjour,

J'ai reçu la facture pour notre dernière commande de fer, mais il y a une incohérence sur le montant total. Pouvez-vous vérifier si toutes les remises appliquées ont bien été prises en compte et m'expliquer cette différence ? J'aimerais également savoir comment procéder au règlement de cette facture.

Dans l'attente de votre réponse rapide.

Cordialement,  
- Marc Lefevre, Responsable comptabilité, BTP Durables"""
]


for i,ticket_i in enumerate (tickets):
    print(f'Le {i}-ème ticket donne la sortie suivante')
    reponse=route(agents,ticket_i)
    print(f"\n La réponse est: \n {reponse} ")

