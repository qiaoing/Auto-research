from __future__ import annotations

import json
from pathlib import Path

import pytest

from local_runner.config import RunnerConfig
from local_runner.api_server import create_app


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative in ("tasks", "logs", "prompts/codex", "prompts/opencode", "results", "figures", "paper"):
        (root / relative).mkdir(parents=True, exist_ok=True)
    (root / "progress.md").write_text("# Progress\n", encoding="utf-8")
    write_queue(root, [])
    return root


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


@pytest.fixture()
def client(repo_root: Path):
    from fastapi.testclient import TestClient

    app = create_app(
        RunnerConfig(
            repo_root=repo_root,
            api_token="test-token",
            webhook_secret="webhook-secret",
        )
    )
    return TestClient(app)


def write_queue(repo_root: Path, tasks: list[dict]) -> None:
    queue_path = repo_root / "tasks" / "task_queue.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        json.dumps({"schema_version": 2, "tasks": tasks}, indent=2),
        encoding="utf-8",
    )


def read_queue(repo_root: Path) -> dict:
    return json.loads((repo_root / "tasks" / "task_queue.json").read_text(encoding="utf-8"))


def find_task(repo_root: Path, task_id: str) -> dict:
    for task in read_queue(repo_root)["tasks"]:
        if task["id"] == task_id:
            return task
    raise AssertionError(f"task not found: {task_id}")
