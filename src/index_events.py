#!/usr/bin/env python3
"""Charge events.json, vectorise tout en un lot, et stocke dans ChromaDB."""
import json

from embed import embed_texts, event_to_text
from vectorstore import get_client, get_collection


def load_events(path="events.json"):
    """Charge la liste d'événements normalisés."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def index_events(events, collection):
    """Vectorise tous les événements en un seul appel, puis les stocke."""
    # 1. Construire tous les textes à vectoriser.
    textes = [event_to_text(e) for e in events]

    # 2. Un seul appel Ollama pour tout le lot.
    print(f"Vectorisation de {len(textes)} événements en un lot...")
    vecteurs = embed_texts(textes)
    print(f"{len(vecteurs)} vecteurs reçus.")

    # 3. Construire les listes pour Chroma.
    ids = [f"evt_{i}" for i in range(len(events))]
    metadatas = [
        {
            "source": e["source"],
            "event_type": e["event_type"],
            "severity": e["severity"],
            "source_ip": e["source_ip"],
            "timestamp": e["timestamp"],
        }
        for e in events
    ]

    # 4. Tout insérer d'un coup.
    collection.add(
        ids=ids,
        documents=textes,
        embeddings=vecteurs,
        metadatas=metadatas,
    )
    print(f"{len(ids)} événements indexés dans ChromaDB.")


if __name__ == "__main__":
    events = load_events()
    print(f"{len(events)} événements chargés depuis events.json.")

    client = get_client()
    collection = get_collection(client)

    # Repartir propre : vider la collection avant de réindexer.
    existing = collection.count()
    if existing > 0:
        print(f"Collection non vide ({existing}), réinitialisation.")
        client.delete_collection(collection.name)
        collection = get_collection(client)

    index_events(events, collection)
    print(f"Total dans la collection : {collection.count()}")
