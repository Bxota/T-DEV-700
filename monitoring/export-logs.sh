#!/bin/bash
# Script d'export des logs brut depuis Docker
# Usage: ./export-logs.sh [service] [depuis]
# Exemple: ./export-logs.sh reverseproxy 24h
#          ./export-logs.sh backend 1h
#          ./export-logs.sh all 30m

cd "$(dirname "$0")/.."

SERVICE="${1:-reverseproxy}"
SINCE="${2:-6h}"
OUTPUT_FILE="monitoring/${SERVICE}-logs-$(date +%Y%m%d-%H%M%S).txt"

echo "Export des logs de '$SERVICE' (depuis ${SINCE})..."

if [ "$SERVICE" = "all" ]; then
  docker-compose logs --no-log-prefix --since "$SINCE" > "$OUTPUT_FILE"
else
  docker-compose logs --no-log-prefix --since "$SINCE" "$SERVICE" > "$OUTPUT_FILE"
fi

if [ -s "$OUTPUT_FILE" ]; then
  LINE_COUNT=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')
  FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  echo "Export terminé : $OUTPUT_FILE"
  echo "   $LINE_COUNT lignes, $FILE_SIZE"
  echo ""
  echo "Aperçu des premières lignes :"
  head -n 3 "$OUTPUT_FILE"
else
  echo " Aucun log trouvé pour '$SERVICE'"
  rm "$OUTPUT_FILE"
fi
