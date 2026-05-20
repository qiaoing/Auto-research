# Cloudflare Tunnel Exposure

The local runner API should keep listening on `127.0.0.1:8765`. Cloudflare Tunnel exposes that local-only service through HTTPS without opening an inbound firewall port.

## Current Smoke-Test Mode

For a temporary public URL that does not require a Cloudflare login:

```powershell
.\scripts\start_cloudflare_quick_tunnel.ps1
```

This prints a random `https://*.trycloudflare.com` URL. It is useful for connectivity tests but has no uptime guarantee and should not be used as the long-term Hermes endpoint.

## Stable Domain Mode

To create `https://auto-runner.qiaoing.work`, first authenticate this machine with Cloudflare:

```powershell
"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel login
```

In the browser, choose the Cloudflare account that manages `qiaoing.work` and authorize it. This creates:

```text
%USERPROFILE%\.cloudflared\cert.pem
```

Then run:

```powershell
cd G:\AI_workspace\localserver
.\scripts\setup_cloudflare_tunnel.ps1
```

The script creates a named tunnel, writes a config file under `%USERPROFILE%\.cloudflared`, and maps:

```text
auto-runner.qiaoing.work -> http://127.0.0.1:8765
```

Start the named tunnel using the command printed by the setup script.

## Hermes Call

After the tunnel is running:

```bash
curl -X POST \
  -H "Authorization: Bearer <LOCAL_RUNNER_API_TOKEN>" \
  https://auto-runner.qiaoing.work/run-once
```

Keep `LOCAL_RUNNER_API_TOKEN` strong. `/health` is public, but `/status`, `/tasks`, `/run-once`, and `/logs/{task_id}` require the bearer token. GitHub webhook calls must use the configured HMAC secret.
