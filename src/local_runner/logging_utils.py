"""Log file utilities for the local runner."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .security import safe_filename_component


def ensure_logs_dir(repo_root: Path) -> Path:
    logs_dir = repo_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def configure_service_logger(repo_root: Path) -> logging.Logger:
    logs_dir = ensure_logs_dir(repo_root)
    logger = logging.getLogger("local_runner.service")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(logs_dir / "local_runner_service.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def task_agent_log_path(repo_root: Path, task_id: str) -> Path:
    return ensure_logs_dir(repo_root) / f"{safe_filename_component(task_id)}_agent.log"


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")


def tail_lines(path: Path, limit: int = 400) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-limit:])


def log_summary(path: Path) -> dict[str, Any]:
    return {"file": str(path.as_posix()), "content": tail_lines(path)}
