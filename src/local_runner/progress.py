"""Append-only progress log helpers."""

from __future__ import annotations

from pathlib import Path

from .time_utils import utc_now_iso


def append_progress(repo_root: Path, message: str) -> None:
    progress_path = repo_root / "progress.md"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    with progress_path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n- {utc_now_iso()} {message}\n")
