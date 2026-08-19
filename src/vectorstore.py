#!/usr/bin/env python3
"""Connexion à ChromaDB et gestion de la collection d'événements."""
import chromadb

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION_NAME = "logsentinel_events"


def get_client():
    """Connecte au ChromaDB qui tourne dans Docker."""
    return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def get_collection(client):
    """Récupère la collection, ou la crée si elle n'existe pas.

    On désactive la fonction d'embedding intégrée de Chroma : on
    fournit nos propres vecteurs (calculés par Ollama).
    """
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Événements de logs normalisés"},
        embedding_function=None,
    )


if __name__ == "__main__":
    client = get_client()
    print("Connexion à ChromaDB établie.")

    # heartbeat : vérifie que le serveur répond
    print(f"Heartbeat : {client.heartbeat()}")

    collection = get_collection(client)
    print(f"Collection '{collection.name}' prête.")
    print(f"Nombre d'éléments actuels : {collection.count()}")
