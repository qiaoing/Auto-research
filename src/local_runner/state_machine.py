"""Task state normalization and transition helpers."""

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from typing import Any

from .time_utils import utc_now_iso

PENDING = "pending"
CLAIMED = "claimed"
RUNNING = "running"
REVIEW = "review"
DONE = "done"
FAILED = "failed"
BLOCKED = "blocked"
CANCELLED = "cancelled"

VALID_STATES = {
    PENDING,
    CLAIMED,
    RUNNING,
    REVIEW,
    DONE,
    FAILED,
    BLOCKED,
    CANCELLED,
}

TERMINAL_LOCAL_STATES = {REVIEW, FAILED, BLOCKED, CANCELLED}

ALLOWED_TRANSITIONS = {
    PENDING: {CLAIMED, BLOCKED, FAILED, CANCELLED},
    CLAIMED: {RUNNING, FAILED, BLOCKED, CANCELLED},
    RUNNING: {REVIEW, FAILED, BLOCKED, CANCELLED},
    REVIEW: {DONE, FAILED, CANCELLED},
    FAILED: {PENDING, CANCELLED},
    BLOCKED: {PENDING, CANCELLED},
    DONE: set(),
    CANCELLED: set(),
}

DEFAULT_MAX_ATTEMPTS = 3


class InvalidTransition(ValueError):
    """Raised when a task transition violates the local state machine."""


def normalize_task(raw_task: dict[str, Any]) -> dict[str, Any]:
    task = deepcopy(raw_task)
    status = task.get("status", task.get("state", PENDING))
    if status not in VALID_STATES:
        status = PENDING
    task["status"] = status
    task.setdefault("attempts", 0)
    task.setdefault("max_attempts", DEFAULT_MAX_ATTEMPTS)
    task.setdefault("changed_files", [])
    task.setdefault("logs", [])
    task.setdefault("last_note", None)
    task.setdefault("last_error", None)
    task.setdefault("last_update", None)
    task.setdefault("claimed_by", None)
    task.setdefault("claimed_at", None)
    task.setdefault("started_at", None)
    task.setdefault("finished_at", None)
    task.setdefault("requires_human_approval", False)
    task.setdefault("assigned_to", "codex")
    task.setdefault("priority", 3)
    return task


def normalize_queue(raw_queue: Any) -> dict[str, Any]:
    if isinstance(raw_queue, list):
        tasks = raw_queue
        metadata: dict[str, Any] = {}
    elif isinstance(raw_queue, dict):
        tasks = raw_queue.get("tasks", [])
        metadata = {key: value for key, value in raw_queue.items() if key != "tasks"}
    else:
        tasks = []
        metadata = {}

    metadata["schema_version"] = max(int(metadata.get("schema_version", 2)), 2)
    metadata["states"] = sorted(VALID_STATES)
    metadata["tasks"] = [normalize_task(task) for task in tasks if isinstance(task, dict)]
    return metadata


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())


def transition_task(task: dict[str, Any], to_status: str, **updates: Any) -> dict[str, Any]:
    if to_status not in VALID_STATES:
        raise InvalidTransition(f"unknown task status: {to_status}")

    current = normalize_task(task)
    from_status = current["status"]
    if from_status != to_status and not can_transition(from_status, to_status):
        raise InvalidTransition(f"cannot transition task from {from_status} to {to_status}")

    updated = deepcopy(current)
    updated.update(updates)
    updated["status"] = to_status
    updated["last_update"] = utc_now_iso()
    return normalize_task(updated)


def count_by_status(tasks: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in sorted(VALID_STATES)}
    for task in tasks:
        status = normalize_task(task)["status"]
        counts[status] = counts.get(status, 0) + 1
    return counts
