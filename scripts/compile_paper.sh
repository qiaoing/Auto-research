#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAIN_TEX="$ROOT_DIR/paper/main.tex"

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "pdflatex is not installed. Skipping paper compilation."
  exit 0
fi

if [ ! -f "$MAIN_TEX" ]; then
  echo "paper/main.tex was not found. Skipping paper compilation."
  exit 0
fi

cd "$ROOT_DIR/paper"
pdflatex -interaction=nonstopmode -halt-on-error main.tex
