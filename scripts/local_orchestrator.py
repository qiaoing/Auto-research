#!/usr/bin/env python3
from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "tasks" / "task_queue.json"
PROGRESS_MD_PATH = ROOT / "progress.md"
LOGS_DIR = ROOT / "logs"


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_progress(entry: str) -> None:
    with PROGRESS_MD_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"- [{timestamp()}] {entry}\n")


def write_log(name: str, command: list[str], result: subprocess.CompletedProcess[str]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / name
    log_path.write_text(
        "\n".join(
            [
                f"time: {timestamp()}",
                f"command: {json.dumps(command, ensure_ascii=False)}",
                f"returncode: {result.returncode}",
                "",
                "stdout:",
                result.stdout,
                "",
                "stderr:",
                result.stderr,
            ]
        ),
        encoding="utf-8",
    )


def load_queue() -> dict[str, Any]:
    with QUEUE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_queue(queue: dict[str, Any]) -> None:
    with QUEUE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(queue, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def pick_next_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    pending = [task for task in tasks if task.get("status") == "pending"]
    if not pending:
        return None
    return sorted(pending, key=lambda item: (int(item.get("priority", 9999)), item.get("id", "")))[0]


def read_prompt(prompt_file: str) -> str:
    prompt_path = ROOT / prompt_file
    return prompt_path.read_text(encoding="utf-8")


def resolve_cli_command(name: str) -> str:
    if sys.platform.startswith("win"):
        for candidate in (f"{name}.cmd", f"{name}.exe", name):
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
        return name

    return shutil.which(name) or name


def normalize_repo_path(path: str) -> str:
    return Path(path).as_posix().lstrip("./")


def expected_output_touched(task: dict[str, Any], changed_files: list[str]) -> bool:
    expected_outputs = task.get("expected_outputs", [])
    if not expected_outputs:
        return True

    expected = {normalize_repo_path(path) for path in expected_outputs}
    changed = {normalize_repo_path(path) for path in changed_files}
    return not expected.isdisjoint(changed)


def build_agent_command(task: dict[str, Any]) -> list[str]:
    assigned_to = str(task.get("assigned_to", "")).strip().lower()
    prompt_text = read_prompt(task["prompt_file"])

    if assigned_to == "codex":
        return [resolve_cli_command("codex"), "exec", "--full-auto", prompt_text]
    if assigned_to == "opencode":
        return [resolve_cli_command("opencode"), "run", prompt_text]
    raise ValueError(f"Unsupported task owner: {assigned_to}")


def normalize_quality_check(command_text: str) -> list[str]:
    parts = shlex.split(command_text, posix=False)
    if not parts:
        raise ValueError("Empty quality check command.")
    if parts[0] == "python":
        return [sys.executable, *parts[1:]]
    if parts[0] == "pytest":
        return [sys.executable, "-m", "pytest", *parts[1:]]
    return parts


def capture_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def run_command(command: list[str], log_name: str) -> subprocess.CompletedProcess[str]:
    result = capture_command(command)
    write_log(log_name, command, result)
    return result


def current_head() -> str | None:
    result = capture_command(["git", "rev-parse", "HEAD"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def changed_files_since(reference_head: str | None) -> list[str]:
    changed_files: set[str] = set()

    if reference_head is not None:
        post_head = current_head()
        if post_head is not None and post_head != reference_head:
            result = capture_command(["git", "diff", "--name-only", f"{reference_head}..{post_head}"])
            if result.returncode == 0:
                changed_files.update(line.strip() for line in result.stdout.splitlines() if line.strip())

    for command in (
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        result = capture_command(command)
        if result.returncode == 0:
            changed_files.update(line.strip() for line in result.stdout.splitlines() if line.strip())

    return sorted(changed_files)


def mark_task(task: dict[str, Any], status: str, note: str) -> None:
    task["status"] = status
    task["last_update"] = timestamp()
    task["last_note"] = note


def main() -> int:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if not QUEUE_PATH.exists():
        print(f"Task queue not found: {QUEUE_PATH}")
        append_progress(f"Task queue missing: {QUEUE_PATH}")
        return 1

    queue = load_queue()
    tasks = queue.get("tasks", [])
    task = pick_next_task(tasks)

    if task is None:
        print("No pending tasks found.")
        append_progress("No pending tasks found in local task queue.")
        return 0

    task_id = task.get("id", "UNKNOWN")
    if task.get("requires_human_approval", False):
        note = f"Task {task_id} blocked because it requires human approval."
        mark_task(task, "blocked", note)
        save_queue(queue)
        append_progress(note)
        return 0

    baseline_head = current_head()
    agent_command = build_agent_command(task)
    task_result = run_command(agent_command, f"{task_id}_agent.log")
    if task_result.returncode != 0:
        note = f"Task {task_id} failed during agent execution."
        mark_task(task, "failed", note)
        save_queue(queue)
        append_progress(note)
        return task_result.returncode

    changed_files = changed_files_since(baseline_head)
    if not expected_output_touched(task, changed_files):
        note = f"Task {task_id} exited successfully but did not modify expected outputs."
        mark_task(task, "failed", note)
        task["changed_files"] = changed_files
        save_queue(queue)
        append_progress(note)
        return 1

    for index, quality_check in enumerate(task.get("quality_checks", []), start=1):
        check_command = normalize_quality_check(quality_check)
        check_result = run_command(check_command, f"{task_id}_check_{index}.log")
        if check_result.returncode != 0:
            note = f"Task {task_id} failed quality check: {quality_check}"
            mark_task(task, "failed", note)
            save_queue(queue)
            append_progress(note)
            return check_result.returncode

    note = f"Task {task_id} completed successfully."
    mark_task(task, "done", note)
    task["changed_files"] = changed_files
    save_queue(queue)
    append_progress(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
