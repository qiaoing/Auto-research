# Local Runner Setup

This guide covers Windows and Linux deployment for the local runner API.

## Install

Use Python 3.10 or newer.

Windows PowerShell:

```powershell
cd G:\AI_workspace\localserver
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux shell:

```sh
cd /path/to/localserver
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If your default package mirror fails, use:

```sh
python -m pip install -i https://pypi.org/simple -r requirements.txt
```

## Environment

Set both secrets before starting the service.

Windows PowerShell:

```powershell
$env:LOCAL_RUNNER_API_TOKEN = "replace-with-a-long-random-token"
$env:GITHUB_WEBHOOK_SECRET = "replace-with-a-long-random-webhook-secret"
```

Linux shell:

```sh
export LOCAL_RUNNER_API_TOKEN="replace-with-a-long-random-token"
export GITHUB_WEBHOOK_SECRET="replace-with-a-long-random-webhook-secret"
```

Optional executor command templates:

```sh
export LOCAL_RUNNER_CODEX_COMMAND='codex exec --cd {repo_root} --prompt-file {prompt_file}'
export LOCAL_RUNNER_OPENCODE_COMMAND='opencode run --prompt-file {prompt_file}'
```

For safe local smoke tests without invoking Codex/OpenCode:

```sh
export LOCAL_RUNNER_AGENT_DRY_RUN=1
```

## Start API

Default host is `127.0.0.1` and default port is `8765`.

Windows PowerShell:

```powershell
.\scripts\run_local_runner_server.ps1
```

Linux shell:

```sh
bash scripts/run_local_runner_server.sh
```

Direct command:

```sh
python scripts/local_runner_server.py --host 127.0.0.1 --port 8765 --repo-root .
```

## Runner Modes

Single pass:

```sh
python scripts/local_runner_service.py --once --repo-root .
```

Polling loop:

```sh
python scripts/local_runner_service.py --interval 30 --repo-root .
```

Each runner pass attempts:

```text
git pull --rebase
python scripts/local_orchestrator.py
git add -A
git commit -m "agent: local runner update"
git push
```

If no remote is configured, pull and push are skipped.

Task `quality_checks` are intentionally restricted. The runner accepts only `pytest` or `python -m pytest` command forms, for example:

```json
{
  "quality_checks": [
    ["python", "-m", "pytest", "-q"]
  ]
}
```

Other command forms are rejected and the task is marked `failed`.

## API Tests

Health does not require auth:

```sh
curl http://127.0.0.1:8765/health
```

Protected endpoints require `Authorization: Bearer <LOCAL_RUNNER_API_TOKEN>`.

Linux shell:

```sh
curl -H "Authorization: Bearer $LOCAL_RUNNER_API_TOKEN" http://127.0.0.1:8765/status
curl -H "Authorization: Bearer $LOCAL_RUNNER_API_TOKEN" http://127.0.0.1:8765/tasks
curl -X POST -H "Authorization: Bearer $LOCAL_RUNNER_API_TOKEN" http://127.0.0.1:8765/run-once
```

Windows PowerShell:

```powershell
curl.exe -H "Authorization: Bearer $env:LOCAL_RUNNER_API_TOKEN" http://127.0.0.1:8765/status
curl.exe -H "Authorization: Bearer $env:LOCAL_RUNNER_API_TOKEN" http://127.0.0.1:8765/tasks
curl.exe -X POST -H "Authorization: Bearer $env:LOCAL_RUNNER_API_TOKEN" http://127.0.0.1:8765/run-once
```

## GitHub Webhook

Configure the repository webhook:

- Payload URL: `https://your-tunnel-domain/webhook/github`
- Content type: `application/json`
- Secret: same value as `GITHUB_WEBHOOK_SECRET`
- Events: just the `push` event

The service only triggers a runner pass when a push changes one of:

- `tasks/`
- `prompts/`
- `project_state.json`
- `AGENTS.md`

## Tunnel

Cloudflare Tunnel:

```sh
cloudflared tunnel --url http://127.0.0.1:8765
```

ngrok:

```sh
ngrok http 8765
```

Use the HTTPS tunnel URL plus `/webhook/github` as the GitHub webhook payload URL.

## Linux systemd User Service

Create `.env` in the repo root with local-only permissions:

```sh
LOCAL_RUNNER_API_TOKEN=replace-with-a-long-random-token
GITHUB_WEBHOOK_SECRET=replace-with-a-long-random-webhook-secret
```

Then run:

```sh
bash scripts/install_local_runner_systemd.sh
```

The script writes `~/.config/systemd/user/auto-research-local-runner.service`, enables it, and starts it.

## Windows Task Scheduler

Create a task that runs at user login:

- Program: `G:\AI_workspace\localserver\.venv\Scripts\python.exe`
- Arguments: `scripts\local_runner_server.py --host 127.0.0.1 --port 8765 --repo-root G:\AI_workspace\localserver`
- Start in: `G:\AI_workspace\localserver`

Set `LOCAL_RUNNER_API_TOKEN` and `GITHUB_WEBHOOK_SECRET` as user environment variables or load them in a protected PowerShell wrapper outside Git.

## Security Notes

- Keep the API bound to `127.0.0.1` unless it is behind an HTTPS tunnel.
- `/health` is the only unauthenticated endpoint.
- `/webhook/github` uses HMAC signature verification instead of bearer token auth.
- Do not expose `/run-once` without bearer token protection.
- Run under a non-admin user.
- Use least-privilege Git credentials.
- Do not store secrets in committed files.
- Generated logs, results, figures, and paper files are not ignored by default because Hermes needs them pushed back through GitHub.
