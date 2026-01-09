# Fully Private PR Preview Environments on a Single Laptop (Docker-only)

This package contains two folders:

- `platform/` : local Git + PR UI (Gitea), CI (Woodpecker), reverse proxy (Traefik), and a webhook-based preview cleaner
- `app/`      : a tiny classic PHP + MySQL app repo configured to build & deploy a preview environment per PR

URLs (no hosts file edits required):
- Gitea:     http://gitea.localhost
- CI:        http://ci.localhost
- Cleaner:   http://cleaner.localhost (optional endpoint)
- PR preview: http://pr-<number>.localhost

> Why `localhost`?
> Any `*.localhost` resolves to 127.0.0.1, so the browser works immediately on a single laptop.

---

## 0) Start the platform stack

```bash
cd platform
cp .env.example .env
# edit .env with random secrets (you will fill OAuth values later)
docker compose -f compose.platform.yml up -d --build
```

Open:
- Traefik dashboard: http://localhost:8080
- Gitea: http://gitea.localhost

---

## 1) Gitea initial setup

1. Open `http://gitea.localhost`
2. Complete the initial setup wizard (SQLite default is OK)
3. Create a user and a repository (call it e.g. `php-preview-demo`)

---

## 2) Create a Gitea OAuth app for Woodpecker

In Gitea:
- User menu (top right) -> **Settings** -> **Applications**
- **Create a new OAuth2 Application**
  - Name: `woodpecker`
  - Redirect URI: `http://ci.localhost/authorize`

Copy:
- Client ID
- Client Secret

Put them into `platform/.env`:
- `WOODPECKER_GITEA_CLIENT=...`
- `WOODPECKER_GITEA_SECRET=...`

Restart Woodpecker server:
```bash
cd platform
docker compose -f compose.platform.yml up -d
```

Now open Woodpecker:
- http://ci.localhost
- Login via Gitea

Enable the `php-preview-demo` repo in Woodpecker.

---

## 3) Push the sample app repo to Gitea

### Create an SSH key on Windows (Git Bash) and this will create a file (~/.ssh/id_ed25519)

  ssh-keygen -t ed25519 -C "dev@local"
  cat ~/.ssh/id_ed25519.pub

### Add your public key to Gitea

In the Gitea web UI:

  -Open http://gitea.localhost/
  -Log in
  -Go to User Settings → SSH Keys
  -Click Add Key
  -Paste your public key (id_ed25519.pub)
  -Save


### Fix SSH hostname resolution for Git Bash (important)

inside the folder ssh you need to create a config file in order to fix the SSH resolution if windows is not able to resolve it for SSH command line.

Edit the file and write the text C:\Users\<YOUR_USER>\.ssh\config (or ~/.ssh/config in Git Bash)

  Host gitea.localhost
    HostName 127.0.0.1
    User git
    Port 2222

Set permissions (Git Bash):

  chmod 600 ~/.ssh/config

Verify SSH authentication:

  ssh -v -p 2222 git@gitea.localhost

From this package root:

```bash
cd app
git init
git add .
git commit -m "Initial commit: php preview demo"
git branch -M main

# add your local gitea remote (create the repo first in the UI)
git remote add origin http://gitea.localhost/<YOUR_USER>/php-preview-demo.git
git push -u origin main
```

---

## 4) Create a webhook to auto-clean previews on PR close/merge

We use a tiny service called `preview-cleaner` that removes containers/volumes by docker-compose project label.
It does not need the repo checked out.

In Gitea repo settings:
- Repository -> **Settings** -> **Webhooks** -> **Add Webhook** -> **Gitea**
- Target URL: `http://cleaner.localhost/`  (just root path, it accepts POST)
- Secret: use the same value as `PREVIEW_WEBHOOK_SECRET` in `platform/.env`
- Trigger events: **Pull Request**
- Save

> When PR is closed (merged counts as closed), Gitea sends action=closed and the cleaner deletes `pr-<number>` stack.

---

## 5) Use it: PR -> Preview URL

1. Create a feature branch:
```bash
git checkout -b feature/demo
# edit app/app/index.php or anything
git commit -am "Change demo"
git push -u origin feature/demo
```

2. Open a Pull Request in Gitea.
3. Woodpecker runs automatically (pull_request event).
4. When pipeline finishes, open:
- `http://pr-<PR_NUMBER>.localhost`
- `http://pr-<PR_NUMBER>-db.localhost`

---

## 6) Close/Merge PR -> environment deleted

- Merge PR (or close it)
- Gitea webhook calls the cleaner
- Cleaner removes:
  - containers
  - networks
  - volumes (database data too)

---

## Notes / Limits (honest)

- Woodpecker reliably triggers on PR open/update. Cleanup on merge/close is handled by the webhook cleaner
  to avoid depending on CI event support for PR-closed.
- This is intentionally laptop-simple (HTTP only). In private cloud you’d add:
  - wildcard DNS
  - TLS
  - access control
