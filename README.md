# Fully Private PR Preview Environment
### Docker · PHP · MySQL · Gitea · Woodpecker · Traefik

![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![PHP](https://img.shields.io/badge/PHP-777BB4?logo=php&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)
![Gitea](https://img.shields.io/badge/Gitea-609926?logo=gitea&logoColor=white)
![Woodpecker CI](https://img.shields.io/badge/Woodpecker%20CI-2B2E4A?logo=woodpeckerci&logoColor=white)
![Traefik](https://img.shields.io/badge/Traefik-24A1C1?logo=traefikproxy&logoColor=white)


---

## 1. Project Purpose

This repository demonstrates a **fully private CI/CD preview environment** that runs entirely on a **single developer machine** using Docker.

Each Pull Request automatically:

- Builds a Docker image
- Creates an isolated application container
- Creates an isolated MySQL database
- Initializes the database using `init.sql`
- Exposes a unique preview URL

When the Pull Request is **merged or closed**, **all related containers, networks, and volumes are deleted automatically**.

This setup mirrors enterprise-grade preview environments (GitLab Review Apps, Vercel previews),
but works **100% locally**, fully offline, and without any external SaaS services.

---

## 2. Key Features

- Self-hosted Git server (**Gitea**)
- Self-hosted CI/CD (**Woodpecker**)
- Reverse proxy & dynamic routing (**Traefik**)
- One isolated preview environment per Pull Request
- Automatic database initialization per PR
- Automatic cleanup on PR close or merge
- No manual steps after initial setup
- Designed for private networks and regulated environments

---

## 3. Architecture Overview

```
Developer → Gitea → Woodpecker CI → Docker Engine
                                 ↓
                         Traefik Reverse Proxy
                                 ↓
                    PR Preview Environments
```

Each Pull Request receives:

- One application container
- One MySQL container
- A dedicated Docker network
- Unique Traefik routing (`pr-<number>.localhost`)

---

## 4. Repository Structure

```
.
├── platform/
│   ├── compose.platform.yml
│   └── preview-cleaner/
│
├── php_mysql_demo_app/
│   ├── Dockerfile
│   ├── compose.preview.yml
│   ├── db/
│   │   └── init/
│   │       └── init.sql
│   └── scripts/
│       ├── deploy-preview.sh
│       └── destroy-preview.sh
│
└── README.md
```

---

## 5. URLs (No Hosts File Needed)

Thanks to the special `.localhost` domain, all URLs resolve automatically to `127.0.0.1`.

- Gitea:        http://gitea.localhost
- Woodpecker:   http://ci.localhost
- Traefik:      http://localhost:8080
- Cleaner:      http://cleaner.localhost
- PR Preview:   http://pr-<PR_NUMBER>.localhost

---

## 6. Start the Platform Stack

```bash
cd platform
cp .env.example .env
# Edit .env and set random secrets (OAuth values will be added later)
docker compose -f compose.platform.yml up -d --build
```

Open Gitea:
```
http://gitea.localhost
```

---

## 7. Gitea Initial Setup

1. Open `http://gitea.localhost`
2. Complete the setup wizard (SQLite default is fine)
3. Create a user
4. Create a repository (e.g. `php-preview-demo`)

---

## 8. Configure OAuth (Gitea → Woodpecker)

In Gitea:

- User Settings → Applications
- Create a new OAuth2 application

Settings:

- Name: `woodpecker`
- Redirect URI: `http://ci.localhost/authorize`

Copy the **Client ID** and **Client Secret** into:

```
platform/.env
WOODPECKER_GITEA_CLIENT=...
WOODPECKER_GITEA_SECRET=...
```

Restart the platform:

```bash
docker compose -f compose.platform.yml up -d
```

Login to Woodpecker:
```
http://ci.localhost
```

Enable your repository.

---

## 9. Push the Demo Application

### Generate SSH Key (Windows / Git Bash)

```bash
ssh-keygen -t ed25519 -C "dev@local"
cat ~/.ssh/id_ed25519.pub
```

### Add SSH Key to Gitea

- User Settings → SSH Keys → Add Key
- Paste your public key

### Fix SSH Resolution on Windows

Create file:

```
~/.ssh/config
```

Content:

```
Host gitea.localhost
  HostName 127.0.0.1
  User git
  Port 2222
```

Permissions:

```bash
chmod 600 ~/.ssh/config
```

Verify:

```bash
ssh -v -p 2222 git@gitea.localhost
```

### Push Repository

```bash
cd php_mysql_demo_app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin http://gitea.localhost/<USER>/php-preview-demo.git
git push -u origin main
```

---

## 10. Preview Cleaner (Auto Cleanup)

A small webhook service (`preview-cleaner`) removes preview stacks on PR close or merge.

In Gitea repository settings:

- Webhooks → Add Webhook → Gitea
- Target URL: `http://cleaner.localhost/`
- Secret: same value as `PREVIEW_WEBHOOK_SECRET` in `.env`
- Trigger: **Pull Request events**

When a PR is closed, the cleaner removes:

- Containers
- Networks
- Volumes

---

## 11. CI/CD Pipeline Flow

### Pull Request Opened

1. Developer opens a PR in Gitea
2. Webhook triggers Woodpecker
3. `pull_request` pipeline starts

### Build

- Docker image built
- Tagged with commit SHA

### Deploy Preview

- Docker Compose project: `pr-<PR_NUMBER>`
- App + DB containers created
- Database initialized via `init.sql`
- Traefik routes traffic automatically

Preview URLs:

```
http://pr-<PR_NUMBER>.localhost
http://pr-<PR_NUMBER>-db.localhost
```

### Pull Request Closed / Merged

- Gitea webhook triggers cleaner
- Preview stack destroyed completely
- No leftovers remain

---

## 12. Why This Matters

This project demonstrates:

- Real CI/CD automation
- Production-like workflows
- Infrastructure as Code
- Safe feature testing
- Zero manual environment management

It can scale to:

- Dedicated servers
- Private cloud
- Kubernetes-based preview environments

---

## 13. Status

✔ PR creation works  
✔ Preview environments created  
✔ Database initialized  
✔ Cleanup on merge/close works  
✔ Fully automated  

---

## 14. Notes / Limits

- HTTP only (no TLS) for laptop simplicity
- Cleanup handled via webhook for reliability
- Designed for private environments

## 15. Security disclaimer
This project is for educational purposes only, do not use this implementation directly in production Real systems.
