#!/usr/bin/env bash
set -euo pipefail

PR="${1:-}"
if [[ -z "$PR" ]]; then
  echo "Usage: $0 <pr_number>"
  exit 1
fi

PROJECT="pr-${PR}"

echo "Destroying preview project: ${PROJECT}"

# Stop & remove containers for this compose project
docker ps -aq --filter "label=com.docker.compose.project=${PROJECT}" \
  | xargs -r docker rm -f

# Remove networks for this compose project
docker network ls -q --filter "label=com.docker.compose.project=${PROJECT}" \
  | xargs -r docker network rm

# Remove volumes for this compose project
docker volume ls -q --filter "label=com.docker.compose.project=${PROJECT}" \
  | xargs -r docker volume rm

echo "Destroyed preview project: ${PROJECT}"
