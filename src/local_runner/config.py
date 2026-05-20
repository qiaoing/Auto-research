"""Configuration helpers for portable local runner deployments."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunnerConfig:
    repo_root: Path
    api_token: str | None
    webhook_secret: str | None
    host: str = "127.0.0.1"
    port: int = 8765


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    explicit = repo_root or os.environ.get("LOCAL_RUNNER_REPO_ROOT") or os.environ.get("LOCALSERVER_REPO_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path.cwd().resolve()


def load_config(repo_root: str | Path | None = None, host: str = "127.0.0.1", port: int = 8765) -> RunnerConfig:
    return RunnerConfig(
        repo_root=resolve_repo_root(repo_root),
        api_token=os.environ.get("LOCAL_RUNNER_API_TOKEN") or os.environ.get("LOCALSERVER_AUTH_TOKEN"),
        webhook_secret=os.environ.get("GITHUB_WEBHOOK_SECRET"),
        host=host,
        port=port,
    )
