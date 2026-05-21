"""Persistent multi-turn Codex conversation state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .security import safe_filename_component
from .time_utils import utc_now_iso

DEFAULT_CODEX_INSTANCE = "default"
MAX_TRANSCRIPT_CHARS = 120_000


def is_codex_assignee(assigned_to: str) -> bool:
    return assigned_to.lower().split(":", 1)[0] == "codex"


def codex_instance_from_task(task: dict[str, Any]) -> str:
    explicit = task.get("codex_instance") or task.get("agent_instance")
    if explicit:
        return safe_filename_component(str(explicit)) or DEFAULT_CODEX_INSTANCE
    assigned_to = str(task.get("assigned_to", "codex"))
    if ":" in assigned_to:
        _, suffix = assigned_to.split(":", 1)
        return safe_filename_component(suffix) or DEFAULT_CODEX_INSTANCE
    return DEFAULT_CODEX_INSTANCE


def conversation_id_from_task(task: dict[str, Any]) -> str | None:
    value = task.get("conversation_id") or task.get("thread_id")
    if value:
        return safe_filename_component(str(value))
    if task.get("multi_turn") is True:
        return codex_instance_from_task(task)
    return None


def is_multi_turn_task(task: dict[str, Any]) -> bool:
    return is_codex_assignee(str(task.get("assigned_to", "codex"))) and conversation_id_from_task(task) is not None


def conversation_dir(repo_root: Path, instance: str, conversation_id: str) -> Path:
    return repo_root / "state" / "codex_sessions" / safe_filename_component(instance) / safe_filename_component(conversation_id)


def transcript_path(repo_root: Path, instance: str, conversation_id: str) -> Path:
    return conversation_dir(repo_root, instance, conversation_id) / "transcript.md"


def metadata_path(repo_root: Path, instance: str, conversation_id: str) -> Path:
    return conversation_dir(repo_root, instance, conversation_id) / "metadata.json"


def load_transcript(repo_root: Path, instance: str, conversation_id: str, max_chars: int = MAX_TRANSCRIPT_CHARS) -> str:
    path = transcript_path(repo_root, instance, conversation_id)
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return "\n\n[... earlier conversation truncated ...]\n\n" + text[-max_chars:]


def append_turn(
    repo_root: Path,
    *,
    instance: str,
    conversation_id: str,
    task_id: str,
    prompt_text: str,
    agent_output: str,
    log_path: Path,
) -> Path:
    path = transcript_path(repo_root, instance, conversation_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now_iso()
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"\n\n## Turn {task_id} — {now}\n\n")
        handle.write("### Hermes/User task\n\n")
        handle.write(prompt_text.strip() or "(empty prompt)")
        handle.write("\n\n### Local Codex output\n\n")
        handle.write((agent_output or "(no output)").strip())
        handle.write("\n")

    meta_path = metadata_path(repo_root, instance, conversation_id)
    metadata: dict[str, Any] = {}
    if meta_path.exists():
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            metadata = {}
    turns = list(metadata.get("turns", []))
    turns.append(
        {
            "task_id": task_id,
            "updated_at": now,
            "log_path": str(log_path.relative_to(repo_root).as_posix()),
        }
    )
    metadata.update(
        {
            "instance": instance,
            "conversation_id": conversation_id,
            "last_task_id": task_id,
            "last_update": now,
            "turns": turns,
        }
    )
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def build_codex_prompt(repo_root: Path, task: dict[str, Any], prompt_text: str) -> str:
    conversation_id = conversation_id_from_task(task)
    if not conversation_id:
        return prompt_text
    instance = codex_instance_from_task(task)
    transcript = load_transcript(repo_root, instance, conversation_id)
    header = f"""You are local Codex instance `{instance}` continuing conversation `{conversation_id}` for repository `{repo_root}`.

This is a multi-turn task. Use the prior transcript as durable conversation context, then answer/act on the new turn. Keep changes scoped to the new task, but preserve decisions, APIs, and assumptions already established in this conversation.
"""
    if transcript.strip():
        return f"{header}\n\n# Prior conversation transcript\n\n{transcript}\n\n# New turn task\n\n{prompt_text}"
    return f"{header}\n\n# New turn task\n\n{prompt_text}"
