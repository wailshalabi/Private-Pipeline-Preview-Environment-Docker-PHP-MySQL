# Demo App (PHP + MySQL) for PR Previews

This folder is meant to be pushed as its **own repo** into your local Gitea.

## What the pipeline does

- On `pull_request`: builds a Docker image and deploys a preview environment using `compose.preview.yml`
- On `pull_request_closed`: destroys the preview environment

## Preview URLs

- App: `http://pr-<PR_NUMBER>.localhost`
- DB UI (Adminer): `http://pr-<PR_NUMBER>-db.localhost`

## Local scripts

From your laptop (outside CI) you can also run:

```bash
./scripts/deploy-preview.sh 1 php-preview-demo:test
./scripts/destroy-preview.sh 1
```

## Notes for Woodpecker v3+

Built-in variables changed:

- Event: `CI_PIPELINE_EVENT`
- PR number: `CI_COMMIT_PULL_REQUEST`

See Woodpecker docs for the full list.
