#!/usr/bin/env python3
"""Transforme un MESSAGE sshd brut en champs structurés."""
import re

# Chaque motif capture l'info utile via des groupes nommés (?P<nom>...).
# On les teste dans l'ordre : le premier qui correspond gagne.
PATTERNS = [
    # Échec sur un utilisateur qui n'existe pas
    (
        "ssh_failed_invalid_user",
        "high",
        re.compile(
            r"Failed password for invalid user (?P<user>\S+) "
            r"from (?P<ip>\d+\.\d+\.\d+\.\d+)"
        ),
    ),
    # Échec sur un utilisateur qui existe (plus grave : compte réel visé)
    (
        "ssh_failed_valid_user",
        "critical",
        re.compile(
            r"Failed password for (?P<user>\S+) "
            r"from (?P<ip>\d+\.\d+\.\d+\.\d+)"
        ),
    ),
    # Détection d'un utilisateur invalide (souvent avant l'échec)
    (
        "ssh_invalid_user",
        "medium",
        re.compile(
            r"Invalid user (?P<user>\S+) "
            r"from (?P<ip>\d+\.\d+\.\d+\.\d+)"
        ),
    ),
    # Connexion réussie (trafic normal)
    (
        "ssh_accepted",
        "info",
        re.compile(
            r"Accepted \S+ for (?P<user>\S+) "
            r"from (?P<ip>\d+\.\d+\.\d+\.\d+)"
        ),
    ),
]


def parse_ssh_message(message):
    """Analyse un MESSAGE sshd. Retourne un dict, ou None si non reconnu."""
    for event_type, severity, pattern in PATTERNS:
        match = pattern.search(message)
        if match:
            return {
                "event_type": event_type,
                "severity": severity,
                "source_ip": match.group("ip"),
                "user": match.group("user"),
            }
    return None   # message non pertinent (Server listening, etc.)


# Test intégré : quelques messages types.
if __name__ == "__main__":
    exemples = [
        "Failed password for invalid user admin from 192.168.1.25 port 47964 ssh2",
        "Failed password for root from 192.168.1.25 port 48008 ssh2",
        "Invalid user oracle from 192.168.1.25 port 32878",
        "Accepted publickey for arth from 192.168.1.25 port 34270 ssh2: ED25519",
        "Server listening on 0.0.0.0 port 22.",
    ]
    for msg in exemples:
        resultat = parse_ssh_message(msg)
        print(f"{msg[:50]:52} -> {resultat}")
