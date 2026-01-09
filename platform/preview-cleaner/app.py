import os, subprocess, json
from http.server import BaseHTTPRequestHandler, HTTPServer

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

def sh(cmd):
    # Run a shell command and return (code, stdout, stderr).
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out.strip(), err.strip()

def cleanup_project(project: str):
    # Remove containers, networks, volumes created by docker compose with this project name.
    # Docker Compose labels containers/volumes/networks with com.docker.compose.project=<project>.
    label = f"com.docker.compose.project={project}"

    # Containers
    code, out, err = sh(["docker", "ps", "-aq", "--filter", f"label={label}"])
    if out:
        ids = out.splitlines()
        sh(["docker", "rm", "-f", *ids])

    # Networks
    code, out, err = sh(["docker", "network", "ls", "-q", "--filter", f"label={label}"])
    if out:
        nets = out.splitlines()
        # ignore failures if network in use
        sh(["docker", "network", "rm", *nets])

    # Volumes
    code, out, err = sh(["docker", "volume", "ls", "-q", "--filter", f"label={label}"])
    if out:
        vols = out.splitlines()
        sh(["docker", "volume", "rm", "-f", *vols])

class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # Simple shared-secret check (header: X-Preview-Secret)
        secret = self.headers.get("X-Preview-Secret", "")
        if not WEBHOOK_SECRET or secret != WEBHOOK_SECRET:
            return self._json(401, {"ok": False, "error": "unauthorized"})

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}

        # Two ways to call:
        # 1) From Gitea webhook (pull_request event): payload has pull_request.number + action
        # 2) Manual: {"project":"pr-123"}
        project = payload.get("project")
        action = payload.get("action")

        if not project:
            pr = payload.get("pull_request") or {}
            number = pr.get("number")
            if number is not None:
                project = f"pr-{number}"

        if not project:
            return self._json(400, {"ok": False, "error": "missing project/pr number"})

        # If called by webhook, only clean up on close/merge-ish actions.
        # Gitea sends pull_request action values like opened, synchronized, reopened, closed, etc.
        if action and action not in ("closed",):
            return self._json(200, {"ok": True, "skipped": True, "reason": f"action={action} does not cleanup"})

        cleanup_project(project)
        return self._json(200, {"ok": True, "project": project, "cleaned": True})

def main():
    port = 8081
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"preview-cleaner listening on :{port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
