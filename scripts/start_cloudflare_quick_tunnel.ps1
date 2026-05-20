$ErrorActionPreference = "Stop"

$Cloudflared = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
if (-not (Test-Path $Cloudflared)) {
  $Cloudflared = "cloudflared"
}

$Origin = if ($env:LOCAL_RUNNER_ORIGIN) { $env:LOCAL_RUNNER_ORIGIN } else { "http://127.0.0.1:8765" }

& $Cloudflared tunnel --url $Origin
