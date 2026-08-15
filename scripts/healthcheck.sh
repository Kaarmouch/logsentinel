#!/usr/bin/env bash
set -euo pipefail

echo "== Conteneurs =="
docker compose ps

echo -e "\n== Ollama =="
curl -sf http://localhost:11434 && echo " OK" || echo "ÉCHEC"

echo -e "\n== ChromaDB =="
curl -sf http://localhost:8000/api/v2/heartbeat && echo " OK" || echo "ÉCHEC"

echo -e "\n== Ressources =="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
