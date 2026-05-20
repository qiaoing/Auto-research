"""Security helpers for task-controlled identifiers and paths."""

from __future__ import annotations

import re
from pathlib import Path

SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.-]+$")


def is_safe_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(SAFE_IDENTIFIER.fullmatch(value))


def safe_filename_component(value: object, fallback: str = "unknown") -> str:
    text = str(value or fallback)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", text)
    safe = safe.strip("._") or fallback
    return safe[:120]


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_prompt_file(repo_root: Path, prompt_file: object) -> Path | None:
    if not isinstance(prompt_file, str) or not prompt_file:
        return None
    raw_path = Path(prompt_file)
    if raw_path.is_absolute():
        return None

    prompts_root = (repo_root / "prompts").resolve()
    candidate = (repo_root / raw_path).resolve()
    if not is_relative_to(candidate, prompts_root):
        return None
    return candidate if candidate.exists() else None
