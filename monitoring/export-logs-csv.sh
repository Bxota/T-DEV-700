#!/bin/bash
# Script d'export des logs nginx en CSV
# Usage: ./export-logs-csv.sh [depuis]
# Exemple: ./export-logs-csv.sh 24h

cd "$(dirname "$0")/.."

SINCE="${1:-6h}"
OUTPUT_FILE="monitoring/nginx-logs-$(date +%Y%m%d-%H%M%S).csv"

echo "Export des logs Nginx en CSV (depuis ${SINCE})..."

# Header CSV
echo "timestamp,method,uri,status,bytes_sent,request_time,remote_addr,user_agent,upstream_time" > "$OUTPUT_FILE"

# Extraction et conversion en CSV
docker-compose logs --no-log-prefix --since "$SINCE" reverseproxy \
  | grep -v 'healthz' \
  | grep '^{"time"' \
  | jq -r '[.time, .method, .uri, .status, .bytes_sent, .request_time, .remote_addr, .user_agent, .upstream_time] | @csv' \
  >> "$OUTPUT_FILE"

if [ $(wc -l < "$OUTPUT_FILE" | tr -d ' ') -gt 1 ]; then
  LINE_COUNT=$(($(wc -l < "$OUTPUT_FILE" | tr -d ' ') - 1))
  FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  echo "Export terminé : $OUTPUT_FILE"
  echo "   $LINE_COUNT lignes, $FILE_SIZE"
  echo ""
  echo "Aperçu (utilisez Excel/LibreOffice pour ouvrir) :"
  head -n 4 "$OUTPUT_FILE" | column -t -s,
else
  echo " Aucun log trouvé"
  rm "$OUTPUT_FILE"
fi
