# PHP + MySQL Preview Environments (Local, Private, Docker-only)

This repo is designed to be pushed into a **local Gitea** instance and used with **Woodpecker CI** to create a
**preview environment per Pull Request** on a single laptop — fully private.

Preview URLs use `*.localhost` which resolves to `127.0.0.1` automatically (no hosts file edits).

## What you get

- PR builds automatically in CI (Woodpecker)
- Each PR spins up a preview environment:
  - `http://pr-<number>.localhost`
  - `http://pr-<number>-db.localhost` (Adminer)
- When the PR is **closed/merged**, a Gitea webhook triggers cleanup (containers + volumes removed)

---

## Prerequisites

- Docker Desktop (or Docker Engine) with Docker Compose plugin
- The `platform/` stack from the companion folder up and running:
  - `http://gitea.localhost`
  - `http://ci.localhost`

---

## How it works (high level)

1. Developer pushes a branch and opens a PR in Gitea.
2. Woodpecker runs `.woodpecker.yml`:
   - builds a Docker image for that PR commit
   - deploys (or updates) a compose project named `pr-<number>`
3. Traefik routes `pr-<number>.localhost` to the PR's containers.
4. When the PR is closed/merged, Gitea calls the **preview-cleaner** webhook which removes the `pr-<number>` stack.

---

## Manual local run (without CI)

```bash
# from repo root:
export PR_NUMBER=999
export APP_IMAGE=php-preview:dev

docker build -t "$APP_IMAGE" .
docker compose -f compose.preview.yml -p "pr-$PR_NUMBER" up -d --build
```

Open:
- http://pr-999.localhost
- http://pr-999-db.localhost

Tear down:
```bash
docker compose -f compose.preview.yml -p "pr-999" down -v
```

---

## Notes

- Database is seeded on first start using `docker/mysql/init.sql`.
- This is a local demo pattern that scales later to bigger VMs/private cloud by replacing:
  - `*.localhost` -> real wildcard DNS like `*.test.internal`
  - docker-compose-per-PR -> Kubernetes namespace per PR (optional future)
