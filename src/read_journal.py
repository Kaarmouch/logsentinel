#!/usr/bin/env python3
"""Lit les événements sshd depuis journald et les affiche en objets Python."""
import subprocess
import json


def read_ssh_events(since="1 day ago"):
    """Récupère les événements sshd de journald sur une période donnée.

    Retourne une liste de dictionnaires, un par événement.
    """
    # On construit la commande journalctl comme une liste d'arguments.
    cmd = [
        "journalctl",
        "_COMM=sshd",
        "-o", "json",
        "--no-pager",
        "--since", since,
    ]

    # subprocess.run exécute la commande et capture sa sortie texte.
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # journalctl produit un objet JSON par ligne. On parse ligne par ligne.
    events = []
    for line in result.stdout.strip().split("\n"):
        if line:                      # ignore les lignes vides
            events.append(json.loads(line))
    return events


# Point d'entrée : ne s'exécute que si on lance le fichier directement.
if __name__ == "__main__":
    events = read_ssh_events()
    print(f"{len(events)} événements sshd récupérés.\n")

    # On affiche les 3 premiers, juste le champ MESSAGE.
    for event in events[-3:]:
        print(event.get("MESSAGE", "(pas de message)"))
