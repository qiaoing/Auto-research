"""Persistent JSON task queue storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .state_machine import normalize_queue, normalize_task

TASK_QUEUE_PATH = Path("tasks") / "task_queue.json"


def queue_path(repo_root: Path) -> Path:
    return repo_root / TASK_QUEUE_PATH


def load_queue(repo_root: Path) -> dict[str, Any]:
    path = queue_path(repo_root)
    if not path.exists():
        return normalize_queue({"schema_version": 2, "tasks": []})

    with path.open("r", encoding="utf-8") as handle:
        raw_queue = json.load(handle)
    return normalize_queue(raw_queue)


def save_queue(repo_root: Path, queue: dict[str, Any]) -> None:
    path = queue_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_queue(queue)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(normalized, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def get_tasks(repo_root: Path) -> list[dict[str, Any]]:
    return load_queue(repo_root)["tasks"]


def replace_task(queue: dict[str, Any], updated_task: dict[str, Any]) -> dict[str, Any]:
    task_id = updated_task.get("id")
    if not task_id:
        raise ValueError("task must have an id")

    normalized = normalize_queue(queue)
    tasks = []
    replaced = False
    for task in normalized["tasks"]:
        if task.get("id") == task_id:
            tasks.append(normalize_task(updated_task))
            replaced = True
        else:
            tasks.append(task)
    if not replaced:
        tasks.append(normalize_task(updated_task))

    normalized["tasks"] = tasks
    return normalized


def summarize_tasks(repo_root: Path) -> list[dict[str, Any]]:
    summaries = []
    for task in get_tasks(repo_root):
        assigned_to = task.get("assigned_to")
        codex_instance = task.get("codex_instance") or task.get("agent_instance")
        if not codex_instance and isinstance(assigned_to, str) and ":" in assigned_to:
            prefix, suffix = assigned_to.split(":", 1)
            if prefix.lower() == "codex":
                codex_instance = suffix or "default"
        conversation_id = task.get("conversation_id") or task.get("thread_id")
        multi_turn = bool(task.get("multi_turn")) or bool(conversation_id)
        summaries.append(
            {
                "id": task.get("id"),
                "title": task.get("title"),
                "assigned_to": assigned_to,
                "status": task.get("status"),
                "priority": task.get("priority"),
                "last_update": task.get("last_update"),
                "last_note": task.get("last_note"),
                "conversation_id": conversation_id,
                "thread_id": task.get("thread_id"),
                "codex_instance": codex_instance,
                "agent_instance": task.get("agent_instance"),
                "multi_turn": multi_turn,
            }
        )
    return summaries
