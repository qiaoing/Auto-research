#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p logs

echo "[Local Research Autopilot] $(date) Pulling latest tasks..." | tee -a logs/local_loop.log
git pull --rebase || true

echo "[Local Research Autopilot] $(date) Running next task..." | tee -a logs/local_loop.log
python scripts/local_orchestrator.py || true

echo "[Local Research Autopilot] $(date) Pushing results..." | tee -a logs/local_loop.log
git add -A
git commit -m "agent: local loop update" || true
git push || true
