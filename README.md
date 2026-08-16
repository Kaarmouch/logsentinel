# LogSentinel

Détecteur d'anomalies dans les logs de sécurité, combinant un SIEM léger
et un LLM exécuté localement. Aucune donnée ne sort de l'infrastructure.

## Objectif

Générer des journaux système (trafic normal + attaques simulées), les
normaliser, les indexer dans une base vectorielle, et utiliser un modèle
de langage local pour qualifier les événements suspects et produire des
explications lisibles.

## Stack

| Composant | Rôle | État |
|---|---|---|
| nginx | Serveur web cible (surface d'attaque web) | En place |
| Ollama | Inférence LLM locale (qwen2.5) | En place |
| ChromaDB | Base vectorielle pour la recherche par similarité | En place |
| Docker Compose | Isolation des services | En place |
| hydra / nmap | Génération d'attaques simulées | En place |
| Script Python | Parsing et normalisation des logs | En place |

## Roadmap

- [x] **Étape 1** — Environnement : VM Ubuntu, Docker, Ollama, ChromaDB
- [x] **Étape 2** — Génération de logs : trafic normal et attaques simulées
- [x] **Étape 3** — Ingestion : script Python de parsing et normalisation
- [ ] **Étape 4** — Vectorisation : embeddings des logs dans ChromaDB
- [ ] **Étape 5** — Détection : analyse LLM et scoring d'anomalie
- [ ] **Étape 6** — Dashboard React/Vite
- [ ] **Étape 7** — Documentation et démo

## Jeu de données de test

Les scripts de `scripts/` génèrent quatre types d'événements, avec IP
source identifiable (attaques lancées depuis l'hôte vers la VM) :

| Source | Normal | Malveillant |
|---|---|---|
| Web (nginx) | `GET /` → 200 | scan 404, path traversal 400, injection SQL/XSS |
| SSH (journald) | `Accepted publickey` | bruteforce `Failed password` (hydra) |

Note : les logs générés contiennent des adresses IP et ne sont **pas**
versionnés (voir `.gitignore`). Seuls les scripts qui les produisent
le sont.

## Démarrage

```bash
cp .env.example .env
docker compose up -d
docker exec -it ollama ollama pull qwen2.5:0.5b
./scripts/healthcheck.sh
```

Les services n'écoutent que sur `127.0.0.1`. Accès depuis un poste distant
par tunnel SSH :

```bash
ssh -L 11434:localhost:11434 -L 8000:localhost:8000 user@host
```

## Environnement de développement

VM VirtualBox 7.0 — Ubuntu Server 24.04, 3 Go RAM, 2 vCPU, disque
dynamique 40 Go, réseau en pont.

## Documentation

- [Journal de bord](docs/journal.md)
- [Décisions techniques](docs/decisions/)
