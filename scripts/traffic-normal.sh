#!/usr/bin/env bash
# Trafic HTTP légitime : requêtes valides, rythme humain
set -euo pipefail

PAGES=("/" "/index.html" "/about" "/contact")
DURATION=${1:-60}   # durée en secondes, 60 par défaut
END=$((SECONDS + DURATION))

echo "Génération de trafic normal pendant ${DURATION}s..."
while [ $SECONDS -lt $END ]; do
  page=${PAGES[$RANDOM % ${#PAGES[@]}]}
  curl -s -o /dev/null "http://localhost${page}"
  sleep "$(awk 'BEGIN{print 0.5 + rand()*2}')"   # pause 0,5–2,5 s
done
echo "Terminé."
