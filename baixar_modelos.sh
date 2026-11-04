#!/usr/bin/env bash
# Baixa cada modelo listado em models.txt para /comfyui/models/<pasta>/<arquivo>
set -euo pipefail
LISTA="$1"
command -v wget >/dev/null || (apt-get update -qq && apt-get install -y -qq wget)
# tr -d '\r' = tolera arquivo salvo no Windows (CRLF)
tr -d '\r' < "$LISTA" | grep -v '^\s*\(#\|$\)' | while read -r URL PASTA ARQ; do
  mkdir -p "/comfyui/models/$PASTA"
  echo ">> $ARQ -> models/$PASTA"
  wget -q --show-progress -O "/comfyui/models/$PASTA/$ARQ" "$URL"
done
