"""GitHub webhook validation and filtering."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any


def verify_github_signature(body: bytes, signature_header: str | None, secret: str | None) -> bool:
    if not secret or not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header, expected)


def changed_paths(payload: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for commit in payload.get("commits", []) or []:
        for key in ("added", "modified", "removed"):
            for path in commit.get(key, []) or []:
                if isinstance(path, str):
                    paths.add(path)
    head_commit = payload.get("head_commit") or {}
    for key in ("added", "modified", "removed"):
        for path in head_commit.get(key, []) or []:
            if isinstance(path, str):
                paths.add(path)
    return paths


def has_relevant_path(paths: set[str]) -> bool:
    return any(path == "project_state.json" or path == "AGENTS.md" or path.startswith(("tasks/", "prompts/")) for path in paths)
