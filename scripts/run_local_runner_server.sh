#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/local_runner_server.py --host "${LOCAL_RUNNER_HOST:-127.0.0.1}" --port "${LOCAL_RUNNER_PORT:-8765}"
