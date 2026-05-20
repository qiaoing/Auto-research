"""Persisted status for API visibility into runner activity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .time_utils import utc_now_iso

STATUS_PATH = Path("logs") / "runner_status.json"


def status_path(repo_root: Path) -> Path:
    return repo_root / STATUS_PATH


def read_runner_status(repo_root: Path) -> dict[str, Any]:
    path = status_path(repo_root)
    if not path.exists():
        return {"current_task": None, "last_run_at": None, "last_run_status": None, "last_run_id": None}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"current_task": None, "last_run_at": None, "last_run_status": "status_read_error", "last_run_id": None}


def write_runner_status(repo_root: Path, **updates: Any) -> dict[str, Any]:
    path = status_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    status = read_runner_status(repo_root)
    status.update(updates)
    status["updated_at"] = utc_now_iso()
    path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return status
