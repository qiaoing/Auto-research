$ErrorActionPreference = "Stop"
$exe = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
$config = "C:\Users\26938\.cloudflared\auto-research-local-runner.yml"
& $exe tunnel --config $config run auto-research-local-runner
