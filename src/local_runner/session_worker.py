"""Conversation-oriented local Codex session store and direct turn execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import git_ops
from .codex_sessions import (
    append_turn,
    build_codex_prompt,
    codex_instance_from_task,
    conversation_dir,
    conversation_id_from_task,
    load_transcript,
    merged_prompt_path,
    metadata_path,
    transcript_path,
)
from .logging_utils import task_agent_log_path
from .orchestrator import TaskExecutionResult, default_task_executor
from .security import safe_filename_component
from .time_utils import utc_now_iso

DEFAULT_SESSION_WORKER = "default"


@dataclass(frozen=True)
class SessionTurnResult:
    conversation_id: str
    turn_id: str
    codex_instance: str
    status: str
    success: bool
    transcript_path: str
    merged_prompt_path: str | None
    log_path: str
    artifact_paths: list[str]
    note: str
    error: str | None = None


def _relative(repo_root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(repo_root.resolve()).as_posix())
    except ValueError:
        return str(path)


def _turn_id(raw: str | None = None) -> str:
    if raw:
        return safe_filename_component(raw)
    compact = utc_now_iso().replace(":", "").replace("-", "").replace(".", "_").replace("Z", "Z")
    return f"turn-{compact}"


def _task_for_turn(
    *,
    conversation_id: str,
    prompt: str,
    codex_instance: str = DEFAULT_SESSION_WORKER,
    turn_id: str | None = None,
    title: str | None = None,
    quality_checks: list[Any] | None = None,
    expected_outputs: list[str] | None = None,
) -> dict[str, Any]:
    safe_conversation_id = safe_filename_component(conversation_id)
    safe_instance = safe_filename_component(codex_instance) or DEFAULT_SESSION_WORKER
    safe_turn_id = _turn_id(turn_id)
    task = {
        "id": safe_turn_id,
        "title": title or safe_turn_id,
        "assigned_to": f"codex:{safe_instance}",
        "codex_instance": safe_instance,
        "conversation_id": safe_conversation_id,
        "turn_id": safe_turn_id,
        "multi_turn": True,
        "status": "pending",
        "inline_prompt": prompt,
        "expected_outputs": expected_outputs or [],
        "quality_checks": quality_checks or [],
    }
    return task


def ensure_session(repo_root: Path, conversation_id: str, codex_instance: str = DEFAULT_SESSION_WORKER) -> dict[str, Any]:
    safe_conversation_id = safe_filename_component(conversation_id)
    safe_instance = safe_filename_component(codex_instance) or DEFAULT_SESSION_WORKER
    cdir = conversation_dir(repo_root, safe_instance, safe_conversation_id)
    cdir.mkdir(parents=True, exist_ok=True)
    tpath = transcript_path(repo_root, safe_instance, safe_conversation_id)
    if not tpath.exists():
        tpath.write_text(f"# Codex session {safe_conversation_id}\n\n", encoding="utf-8", newline="\n")
    mpath = metadata_path(repo_root, safe_instance, safe_conversation_id)
    if not mpath.exists():
        mpath.write_text(
            "{\n"
            f"  \"instance\": \"{safe_instance}\",\n"
            f"  \"conversation_id\": \"{safe_conversation_id}\",\n"
            "  \"status\": \"active\",\n"
            f"  \"created_at\": \"{utc_now_iso()}\",\n"
            f"  \"last_update\": \"{utc_now_iso()}\",\n"
            "  \"turns\": [],\n"
            "  \"artifacts\": []\n"
            "}\n",
            encoding="utf-8",
        )
    return session_summary(repo_root, safe_conversation_id, safe_instance)


def session_summary(repo_root: Path, conversation_id: str, codex_instance: str = DEFAULT_SESSION_WORKER) -> dict[str, Any]:
    safe_conversation_id = safe_filename_component(conversation_id)
    safe_instance = safe_filename_component(codex_instance) or DEFAULT_SESSION_WORKER
    cdir = conversation_dir(repo_root, safe_instance, safe_conversation_id)
    tpath = transcript_path(repo_root, safe_instance, safe_conversation_id)
    mpath = metadata_path(repo_root, safe_instance, safe_conversation_id)
    metadata: dict[str, Any] = {}
    if mpath.exists():
        import json

        try:
            metadata = json.loads(mpath.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - corrupt metadata should not hide transcript.
            metadata = {}
    return {
        "conversation_id": safe_conversation_id,
        "codex_instance": safe_instance,
        "status": metadata.get("status", "active" if cdir.exists() else "missing"),
        "turn_count": len(metadata.get("turns", [])) if isinstance(metadata.get("turns"), list) else 0,
        "last_update": metadata.get("last_update"),
        "transcript_path": _relative(repo_root, tpath),
        "metadata_path": _relative(repo_root, mpath),
        "exists": cdir.exists(),
    }


def append_session_turn(
    repo_root: Path,
    *,
    conversation_id: str,
    prompt: str,
    codex_instance: str = DEFAULT_SESSION_WORKER,
    turn_id: str | None = None,
    title: str | None = None,
    quality_checks: list[Any] | None = None,
    expected_outputs: list[str] | None = None,
    executor=default_task_executor,
) -> SessionTurnResult:
    """Append one live turn to a local Codex conversation and execute it immediately.

    This bypasses the Git task queue while reusing the existing Codex prompt merge,
    execution, transcript, and logging code paths. It intentionally does not accept
    arbitrary shell commands from HTTP callers.
    """

    repo_root = repo_root.resolve()
    task = _task_for_turn(
        conversation_id=conversation_id,
        prompt=prompt,
        codex_instance=codex_instance,
        turn_id=turn_id,
        title=title,
        quality_checks=quality_checks,
        expected_outputs=expected_outputs,
    )
    safe_conversation_id = conversation_id_from_task(task) or safe_filename_component(conversation_id)
    safe_instance = codex_instance_from_task(task)
    ensure_session(repo_root, safe_conversation_id, safe_instance)

    before_files = set(git_ops.changed_files(repo_root)) if git_ops.is_git_repo(repo_root) else set()
    execution: TaskExecutionResult = executor(repo_root, task)
    after_files = set(git_ops.changed_files(repo_root)) if git_ops.is_git_repo(repo_root) else set()
    artifact_paths = sorted(after_files | before_files)

    prompt_text = str(task.get("inline_prompt", prompt))
    if not transcript_path(repo_root, safe_instance, safe_conversation_id).read_text(encoding="utf-8", errors="replace").count(
        f"## Turn {task['id']}"
    ):
        append_turn(
            repo_root,
            instance=safe_instance,
            conversation_id=safe_conversation_id,
            task_id=str(task["id"]),
            prompt_text=prompt_text,
            agent_output=execution.log_path.read_text(encoding="utf-8", errors="replace") if execution.log_path.exists() else execution.note,
            log_path=execution.log_path,
        )

    merged_path = merged_prompt_path(repo_root, safe_instance, safe_conversation_id, str(task["id"]))
    log_path = execution.log_path if execution.log_path else task_agent_log_path(repo_root, str(task["id"]))
    return SessionTurnResult(
        conversation_id=safe_conversation_id,
        turn_id=str(task["id"]),
        codex_instance=safe_instance,
        status="review" if execution.success else "failed",
        success=execution.success,
        transcript_path=_relative(repo_root, transcript_path(repo_root, safe_instance, safe_conversation_id)) or "",
        merged_prompt_path=_relative(repo_root, merged_path) if merged_path.exists() else None,
        log_path=_relative(repo_root, log_path) or "",
        artifact_paths=artifact_paths,
        note=execution.note,
        error=execution.error,
    )


def read_session_transcript(repo_root: Path, conversation_id: str, codex_instance: str = DEFAULT_SESSION_WORKER) -> dict[str, Any]:
    safe_conversation_id = safe_filename_component(conversation_id)
    safe_instance = safe_filename_component(codex_instance) or DEFAULT_SESSION_WORKER
    return {
        "conversation_id": safe_conversation_id,
        "codex_instance": safe_instance,
        "transcript": load_transcript(repo_root, safe_instance, safe_conversation_id, max_chars=1_000_000),
        "transcript_path": _relative(repo_root, transcript_path(repo_root, safe_instance, safe_conversation_id)),
    }


def build_inline_prompt_for_tests(repo_root: Path, conversation_id: str, prompt: str, codex_instance: str = DEFAULT_SESSION_WORKER) -> str:
    task = _task_for_turn(conversation_id=conversation_id, prompt=prompt, codex_instance=codex_instance)
    return build_codex_prompt(repo_root, task, prompt)
