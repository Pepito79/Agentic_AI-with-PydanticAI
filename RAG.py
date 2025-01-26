#!/usr/bin/env python3
import chromadb
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv
import os
import chromadb.utils.embedding_functions as embedding_functions

"""INITIALIZE THE ENV AND API KEYS"""
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.getenv("GEMINI_API_KEY"))

"""INITIALIZE THE DB AND THE CLIENT """
chroma_client= chromadb.Client()
collection = chroma_client.get_or_create_collection(name="rag")


def split_text(text,chunk_size,chunk_overlap) -> List:
    """Function that split text """
    chunks=[]
    start=0
    while start < len(text):
        end= start + chunk_size
        chunks.append(text[start:end])
        start= end - chunk_overlap
    return chunks

def embedding(text:str):
    """Embedd a text wtith the GEMINI embedding"""
    result=genai.embed_content(
        model="models/text-embedding-004",
        content=text)
    return result['embedding']

def stock_DB(liste: List):
    """Stock the chunks in the db by using the GEMINI embedding"""
    for i in range(len(liste)):
        collection.upsert(
            [
                {
                    "id": f"id{i}",
                    "embedding": embedding(liste[i]),
                    "metadata":{"texte": liste[i]}
                }
            ]
        )
    return collection

def get_metadata_from_query(query:str , top_n):
    query_embedding= embedding(query)
    result= collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n,
        include=["metadata"]
    )
    final=result["metadatas"][0]
    return final 

def main():
    texte= input("entrez le texte a stocker svp")
    chunk_list=split_text(texte,5,2)
    stock_DB(chunk_list)
    query= input("posez votre question")
    return query




if __name__=="__main__":
    print(main())