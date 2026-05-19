#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <prompt-file>" >&2
  exit 1
fi

PROMPT_FILE="$1"
if [ ! -f "$PROMPT_FILE" ]; then
  echo "Prompt file not found: $PROMPT_FILE" >&2
  exit 1
fi

exec codex exec --full-auto "$(cat "$PROMPT_FILE")"
