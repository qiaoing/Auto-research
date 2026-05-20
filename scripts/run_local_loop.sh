#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p logs

echo "[Local Research Autopilot] $(date) Pulling latest tasks..." | tee -a logs/local_loop.log
git pull --rebase || true

echo "[Local Research Autopilot] $(date) Running local runner service once..." | tee -a logs/local_loop.log
python scripts/local_runner_service.py --once || true
