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

## If DNS Is Not Hosted By Cloudflare

If `nslookup -type=NS qiaoing.work` shows non-Cloudflare nameservers, such as DNSPod, Cloudflare cannot publish the public DNS record for you.

For this tunnel, add this CNAME record at the active DNS provider:

```text
Name: auto-runner
Type: CNAME
Value: eb724d5c-2e27-4405-8669-438d8ef5a213.cfargotunnel.com
TTL: 600
```

After DNS propagation, verify:

```powershell
nslookup auto-runner.qiaoing.work 1.1.1.1
curl.exe https://auto-runner.qiaoing.work/health
```

The local tunnel process must still be running:

```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --config "C:\Users\26938\.cloudflared\auto-research-local-runner.yml" run auto-research-local-runner
```

## Hermes Call

After the tunnel is running:

```bash
curl -X POST \
  -H "Authorization: Bearer <LOCAL_RUNNER_API_TOKEN>" \
  https://auto-runner.qiaoing.work/run-once
```

Keep `LOCAL_RUNNER_API_TOKEN` strong. `/health` is public, but `/status`, `/tasks`, `/run-once`, and `/logs/{task_id}` require the bearer token. GitHub webhook calls must use the configured HMAC secret.
