#!/usr/bin/env bash
set -euo pipefail

PR_NUMBER="${1:-}"
if [[ -z "$PR_NUMBER" ]]; then
  echo "Usage: ./scripts/deploy-preview.sh <pr-number> <image-tag>"
  echo "Example: ./scripts/deploy-preview.sh 123 php-preview:pr-123-abcdef"
  exit 1
fi

APP_IMAGE="${2:-}"
if [[ -z "$APP_IMAGE" ]]; then
  echo "Missing image tag."
  exit 1
fi

export PR_NUMBER
export APP_IMAGE

docker compose -f compose.preview.yml -p "pr-${PR_NUMBER}" up -d
echo "Preview URL: http://pr-${PR_NUMBER}.localhost"
