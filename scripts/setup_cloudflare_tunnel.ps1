$ErrorActionPreference = "Stop"

$Cloudflared = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
if (-not (Test-Path $Cloudflared)) {
  $Cloudflared = "cloudflared"
}

$TunnelName = if ($env:LOCAL_RUNNER_TUNNEL_NAME) { $env:LOCAL_RUNNER_TUNNEL_NAME } else { "auto-research-local-runner" }
$Hostname = if ($env:LOCAL_RUNNER_PUBLIC_HOSTNAME) { $env:LOCAL_RUNNER_PUBLIC_HOSTNAME } else { "auto-runner.qiaoing.work" }
$Origin = if ($env:LOCAL_RUNNER_ORIGIN) { $env:LOCAL_RUNNER_ORIGIN } else { "http://127.0.0.1:8765" }
$CloudflaredDir = Join-Path $env:USERPROFILE ".cloudflared"
$ConfigPath = Join-Path $CloudflaredDir "auto-research-local-runner.yml"

New-Item -ItemType Directory -Force -Path $CloudflaredDir | Out-Null

if (-not (Test-Path (Join-Path $CloudflaredDir "cert.pem"))) {
  Write-Host "Cloudflare origin certificate not found. Run this first and authorize qiaoing.work:"
  Write-Host "`"$Cloudflared`" tunnel login"
  exit 1
}

$existing = & $Cloudflared tunnel list 2>$null | Select-String $TunnelName
if (-not $existing) {
  & $Cloudflared tunnel create $TunnelName
}

$tunnelInfo = & $Cloudflared tunnel list | Select-String $TunnelName | Select-Object -First 1
if (-not $tunnelInfo) {
  throw "Tunnel was not found after create: $TunnelName"
}

$credentials = Get-ChildItem $CloudflaredDir -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $credentials) {
  throw "Tunnel credentials JSON not found in $CloudflaredDir"
}

@"
tunnel: $TunnelName
credentials-file: $($credentials.FullName)

ingress:
  - hostname: $Hostname
    service: $Origin
  - service: http_status:404
"@ | Set-Content -Encoding UTF8 $ConfigPath

& $Cloudflared tunnel route dns $TunnelName $Hostname

Write-Host "Cloudflare Tunnel configured."
Write-Host "Config: $ConfigPath"
Write-Host "Run:"
Write-Host "`"$Cloudflared`" tunnel --config `"$ConfigPath`" run $TunnelName"
