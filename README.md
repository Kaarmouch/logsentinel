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
| Ollama | Inférence LLM et embeddings locaux | En place |
| ChromaDB | Base vectorielle pour la recherche par similarité | En place |
| Docker Compose | Isolation des services | En place |
| hydra / nmap | Génération d'attaques simulées | En place |
| Script Python | Parsing et normalisation des logs | En place |
| React / Vite | Dashboard des alertes | En cours |

## Roadmap

- [x] **Étape 1** — Environnement : VM Ubuntu, Docker, Ollama, ChromaDB
- [x] **Étape 2** — Génération de logs : trafic normal et attaques simulées
- [x] **Étape 3** — Ingestion : script Python de parsing et normalisation
- [~] **Étape 4** — Vectorisation : embeddings dans ChromaDB
      (fonctionnel, mis en pause — voir note performance)
- [ ] **Étape 5** — Détection : analyse LLM sur les IP signalées
- [ ] **Étape 6** — Dashboard React/Vite
- [ ] **Étape 7** — Documentation et démo

## Architecture retenue

Le tri rapide est fait par des **règles déterministes** (parsing +
seuils dans `analyze.py`) ; l'**IA** n'intervient qu'en second étage,
sur les événements déjà signalés comme suspects — pas sur l'ensemble du
flux. Ce découpage évite d'appeler un LLM là où un regex suffit.

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

## Note performance (étape 4)

La vectorisation tourne sur CPU (2 vCPU, pas de GPU en VM) : ~1,4 s par
embedding, soit ~5 min pour 232 événements. C'est une limite matérielle.
Le code fonctionne ; l'indexation massive est réservée à un hardware
adapté (VPS ou GPU hors VM). L'analyse LLM cible donc les IP déjà
signalées plutôt que l'ensemble des logs.

## Démarrage

```bash
cp .env.example .env
docker compose up -d
docker exec -it ollama ollama pull qwen2.5:0.5b
docker exec -it ollama ollama pull nomic-embed-text
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
