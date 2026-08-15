#!/usr/bin/env bash
# Requêtes web malveillantes : chemins sensibles, injections, path traversal.
# Chaque motif correspond à une classe d'attaque réelle.
set -euo pipefail

BASE="http://localhost"

# Chemins "simples" : scan de fichiers et d'endpoints sensibles.
PATHS=(
  "/admin"
  "/wp-login.php"
  "/.env"
  "/.git/config"
  "/phpmyadmin"
)

# Motifs "complexes" : contiennent des caractères spéciaux.
# --data-urlencode et --path-as-is empêchent curl de les altérer.
echo "== Scan de fichiers sensibles =="
for p in "${PATHS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}${p}")
  printf "%s  %s\n" "$code" "$p"
  sleep 0.3
done

echo -e "\n== Path traversal (--path-as-is préserve les ../) =="
code=$(curl -s -o /dev/null -w "%{http_code}" --path-as-is "${BASE}/../../etc/passwd")
printf "%s  %s\n" "$code" "/../../etc/passwd"
sleep 0.3

echo -e "\n== Injection SQL (chaîne encodée) =="
code=$(curl -s -o /dev/null -w "%{http_code}" -G "${BASE}/index.php" \
  --data-urlencode "id=1' OR '1'='1")
printf "%s  %s\n" "$code" "/index.php?id=1' OR '1'='1"
sleep 0.3

echo -e "\n== XSS (chaîne encodée) =="
code=$(curl -s -o /dev/null -w "%{http_code}" -G "${BASE}/search" \
  --data-urlencode "q=<script>alert(1)</script>")
printf "%s  %s\n" "$code" "/search?q=<script>alert(1)</script>"

echo -e "\nTerminé."
