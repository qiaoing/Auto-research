$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$hostName = if ($env:LOCAL_RUNNER_HOST) { $env:LOCAL_RUNNER_HOST } else { "127.0.0.1" }
$port = if ($env:LOCAL_RUNNER_PORT) { $env:LOCAL_RUNNER_PORT } else { "8765" }
python scripts/local_runner_server.py --host $hostName --port $port
