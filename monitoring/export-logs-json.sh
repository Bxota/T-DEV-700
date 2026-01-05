#!/bin/bash
# Script d'export des logs nginx en JSON formaté
# Usage: ./export-logs-json.sh [depuis]
# Exemple: ./export-logs-json.sh 24h

cd "$(dirname "$0")/.."

SINCE="${1:-6h}"
OUTPUT_FILE="monitoring/nginx-logs-$(date +%Y%m%d-%H%M%S).json"

echo "Export des logs Nginx en JSON (depuis ${SINCE})..."

# Extraction et formatage des logs JSON nginx
docker-compose logs --no-log-prefix --since "$SINCE" reverseproxy \
  | grep -v 'healthz' \
  | grep '^{"time"' \
  | jq -c '.' > "$OUTPUT_FILE"

if [ -s "$OUTPUT_FILE" ]; then
  LINE_COUNT=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')
  FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  echo "Export terminé : $OUTPUT_FILE"
  echo "   $LINE_COUNT entrées, $FILE_SIZE"
  echo ""
  echo "Aperçu des premières lignes :"
  head -n 3 "$OUTPUT_FILE" | jq -C '.'
else
  echo " Aucun log trouvé"
  rm "$OUTPUT_FILE"
fi
