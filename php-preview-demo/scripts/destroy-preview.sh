#!/usr/bin/env bash
set -euo pipefail

PR_NUMBER="${1:-}"
if [[ -z "$PR_NUMBER" ]]; then
  echo "Usage: ./scripts/destroy-preview.sh <pr-number>"
  exit 1
fi

docker compose -f compose.preview.yml -p "pr-${PR_NUMBER}" down -v
echo "Destroyed preview pr-${PR_NUMBER}"
