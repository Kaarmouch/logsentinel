#!/usr/bin/env python3
"""Transforme des textes en vecteurs (embeddings) via Ollama, par lot."""
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"


def embed_texts(texts):
    """Vectorise une LISTE de textes en un seul appel. Retourne une liste
    de vecteurs, dans le même ordre. Lève une exception en cas d'échec."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": EMBED_MODEL, "input": texts},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def event_to_text(event):
    """Construit le texte à vectoriser à partir d'un événement normalisé."""
    return (
        f"[{event['source']}] {event['event_type']} "
        f"(severity={event['severity']}) "
        f"from {event['source_ip']}: {event['raw']}"
    )


if __name__ == "__main__":
    exemples = [
        "Failed password for invalid user admin from 192.168.1.25",
        "Accepted publickey for arth from 192.168.1.25",
        "GET /.env HTTP/1.1 404",
    ]
    vecteurs = embed_texts(exemples)
    print(f"{len(vecteurs)} vecteurs reçus.")
    print(f"Dimension du premier : {len(vecteurs[0])}")
