# LogSentinel

Détecteur d'anomalies dans les logs de sécurité, combinant un SIEM léger
et un LLM exécuté localement.

## Objectif

Collecter des journaux système authentiques (tentatives d'intrusion SSH,
scans de ports), les indexer, et utiliser un modèle de langage local pour
qualifier les événements et produire des synthèses lisibles — sans qu'aucune
donnée ne sorte de l'infrastructure.

## Architecture

| Composant | Rôle |
|---|---|
| Promtail | Collecte et étiquetage des logs système |
| Loki | Stockage et requêtage (LogQL) |
| Ollama | Inférence LLM locale |
| ChromaDB | Base vectorielle pour la recherche sémantique |

## État d'avancement

- [x] Étape 1 — Socle : VM Ubuntu, Docker, Ollama, ChromaDB
- [ ] Étape 2 — Collecte : Promtail, Loki, Grafana
- [ ] Étape 3 — Pipeline d'analyse
- [ ] Étape 4 — Déploiement VPS et logs réels

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

VM VirtualBox — Ubuntu Server 24.04, 3 Go RAM, 2 vCPU, réseau ponté.

## Documentation

- [Journal de bord](docs/journal.md)
- [Décisions techniques](docs/decisions/)
