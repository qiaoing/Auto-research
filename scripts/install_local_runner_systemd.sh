#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
service_dir="${HOME}/.config/systemd/user"
service_file="${service_dir}/auto-research-local-runner.service"
python_bin="${PYTHON_BIN:-${repo_root}/.venv/bin/python}"

mkdir -p "$service_dir"

cat > "$service_file" <<SERVICE
[Unit]
Description=Auto Research Local Runner API
After=network-online.target

[Service]
Type=simple
WorkingDirectory=${repo_root}
EnvironmentFile=-${repo_root}/.env
ExecStart=${python_bin} scripts/local_runner_server.py --host 127.0.0.1 --port 8765 --repo-root ${repo_root}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
SERVICE

systemctl --user daemon-reload
systemctl --user enable --now auto-research-local-runner.service
systemctl --user status auto-research-local-runner.service --no-pager
