"""Single-pass local task orchestrator."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import git_ops
from .codex_sessions import (
    append_turn,
    build_codex_prompt,
    codex_instance_from_task,
    conversation_id_from_task,
    is_codex_assignee,
    is_multi_turn_task,
    merged_prompt_path,
    transcript_path,
)
from .logging_utils import append_text, task_agent_log_path, task_orchestrator_log_path
from .progress import append_progress
from .security import resolve_prompt_file, safe_filename_component
from .state_machine import BLOCKED, CLAIMED, FAILED, PENDING, REVIEW, RUNNING, normalize_task, transition_task
from .task_store import load_queue, replace_task, save_queue
from .time_utils import utc_now_iso


@dataclass
class TaskExecutionResult:
    success: bool
    log_path: Path
    note: str
    error: str | None = None


TaskExecutor = Callable[[Path, dict[str, Any]], TaskExecutionResult]


def _priority_key(task: dict[str, Any]) -> tuple[int, str]:
    priority = task.get("priority", 3)
    try:
        numeric_priority = int(priority)
    except (TypeError, ValueError):
        numeric_priority = 3
    return numeric_priority, str(task.get("id", ""))


def select_pending_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    pending = [normalize_task(task) for task in tasks if normalize_task(task)["status"] == PENDING]
    if not pending:
        return None
    return sorted(pending, key=_priority_key)[0]


def _prompt_path(repo_root: Path, task: dict[str, Any]) -> Path | None:
    explicit = task.get("prompt_file")
    if explicit:
        return resolve_prompt_file(repo_root, explicit)
    task_id = task.get("id")
    assigned_to = task.get("assigned_to", "codex")
    if not task_id:
        return None
    candidate = repo_root / "prompts" / safe_filename_component(assigned_to) / f"{safe_filename_component(task_id)}.md"
    return candidate if candidate.exists() else None


def _command_from_template(template: str, task: dict[str, Any], repo_root: Path, log_path: Path) -> list[str]:
    prompt_path = _prompt_path(repo_root, task)
    codex_instance = codex_instance_from_task(task)
    conversation_id = conversation_id_from_task(task) or ""
    merged_prompt_file = task.get("_merged_prompt_file") or ""
    values = {
        "task_id": str(task.get("id", "")),
        "prompt_file": str(prompt_path or ""),
        "merged_prompt_file": str(merged_prompt_file),
        "conversation_id": conversation_id,
        "thread_id": str(task.get("thread_id") or ""),
        "codex_instance": codex_instance,
        "agent_instance": codex_instance,
        "multi_turn": str(bool(is_multi_turn_task(task))).lower(),
        "repo_root": str(repo_root),
        "log_file": str(log_path),
    }
    return shlex.split(template.format(**values), posix=os.name != "nt")


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _run_capture(command: list[str], repo_root: Path, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=_subprocess_env(),
    )


def _codex_command(executable: str, repo_root: Path) -> list[str]:
    base_args = shlex.split(os.environ.get("LOCAL_RUNNER_CODEX_ARGS", "exec"), posix=os.name != "nt")
    if not base_args:
        base_args = ["exec"]
    if "--cd" not in base_args:
        base_args.extend(["--cd", str(repo_root)])
    # Use stdin prompt mode to avoid Windows command-line length limits on large merged prompts.
    return [executable, *base_args, "-"]


def _write_merged_prompt_file(repo_root: Path, task: dict[str, Any], merged_prompt: str) -> Path | None:
    if not is_multi_turn_task(task):
        return None
    conversation_id = conversation_id_from_task(task)
    if not conversation_id:
        return None
    instance = codex_instance_from_task(task)
    task_id = str(task.get("id", "unknown"))
    path = merged_prompt_path(repo_root, instance, conversation_id, task_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(merged_prompt, encoding="utf-8", newline="\n")
    return path


def default_task_executor(repo_root: Path, task: dict[str, Any]) -> TaskExecutionResult:
    task_id = str(task.get("id", "unknown"))
    assigned_to = str(task.get("assigned_to", "codex")).lower()
    agent_kind = assigned_to.split(":", 1)[0]
    log_path = task_agent_log_path(repo_root, task_id)
    append_text(log_path, f"{utc_now_iso()} starting {assigned_to} task {task_id}")

    if os.environ.get("LOCAL_RUNNER_AGENT_DRY_RUN") == "1":
        append_text(log_path, f"{utc_now_iso()} dry-run completed for {task_id}")
        if is_multi_turn_task(task):
            prompt_path = _prompt_path(repo_root, task)
            prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path and prompt_path.exists() else str(task.get("title", task_id))
            append_turn(
                repo_root,
                instance=codex_instance_from_task(task),
                conversation_id=conversation_id_from_task(task) or codex_instance_from_task(task),
                task_id=task_id,
                prompt_text=prompt_text,
                agent_output="dry-run agent execution completed",
                log_path=log_path,
            )
        return TaskExecutionResult(True, log_path, "dry-run agent execution completed")

    env_template_name = "LOCAL_RUNNER_OPENCODE_COMMAND" if agent_kind == "opencode" else "LOCAL_RUNNER_CODEX_COMMAND"
    template = os.environ.get(env_template_name)
    prompt_path = _prompt_path(repo_root, task)
    prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path and prompt_path.exists() else str(task.get("title", task_id))
    merged_prompt = build_codex_prompt(repo_root, task, prompt_text) if is_codex_assignee(assigned_to) else prompt_text
    merged_prompt_file = _write_merged_prompt_file(repo_root, task, merged_prompt)
    if merged_prompt_file is not None:
        task["_merged_prompt_file"] = str(merged_prompt_file)

    use_stdin_prompt = False
    if template:
        command = _command_from_template(template, task, repo_root, log_path)
    elif agent_kind == "opencode":
        executable = shutil.which("opencode")
        if not executable:
            message = "opencode executable not found; set LOCAL_RUNNER_OPENCODE_COMMAND or enable dry-run"
            append_text(log_path, message)
            return TaskExecutionResult(False, log_path, "agent command unavailable", message)
        command = [executable, "run"]
        if prompt_path:
            command.extend(["--prompt-file", str(prompt_path)])
    elif is_codex_assignee(assigned_to):
        executable = shutil.which("codex")
        if not executable:
            message = "codex executable not found; set LOCAL_RUNNER_CODEX_COMMAND or enable dry-run"
            append_text(log_path, message)
            return TaskExecutionResult(False, log_path, "agent command unavailable", message)
        command = _codex_command(executable, repo_root)
        use_stdin_prompt = True
    else:
        message = f"unsupported assigned_to value: {assigned_to}"
        append_text(log_path, message)
        return TaskExecutionResult(False, log_path, "agent command unavailable", message)

    result = _run_capture(command, repo_root, input_text=merged_prompt if use_stdin_prompt else None)
    append_text(log_path, result.stdout)
    if result.returncode != 0:
        return TaskExecutionResult(False, log_path, "agent execution failed", result.stdout.strip())
    if is_multi_turn_task(task) and is_codex_assignee(assigned_to):
        append_turn(
            repo_root,
            instance=codex_instance_from_task(task),
            conversation_id=conversation_id_from_task(task) or codex_instance_from_task(task),
            task_id=task_id,
            prompt_text=prompt_text,
            agent_output=result.stdout,
            log_path=log_path,
        )
    return TaskExecutionResult(True, log_path, "agent execution completed")


def _record_multi_turn_if_needed(repo_root: Path, task: dict[str, Any], execution: TaskExecutionResult) -> None:
    if not is_multi_turn_task(task):
        return
    instance = codex_instance_from_task(task)
    conversation_id = conversation_id_from_task(task)
    if not conversation_id:
        return
    path = transcript_path(repo_root, instance, conversation_id)
    task_id = str(task.get("id", "unknown"))
    if path.exists() and f"## Turn {task_id}" in path.read_text(encoding="utf-8", errors="replace"):
        return
    merged_prompt_file = task.get("_merged_prompt_file")
    if isinstance(merged_prompt_file, str) and merged_prompt_file:
        prompt_path = Path(merged_prompt_file)
    else:
        prompt_path = _prompt_path(repo_root, task)
    prompt_text = prompt_path.read_text(encoding="utf-8", errors="replace") if prompt_path and prompt_path.exists() else str(task.get("title", task_id))
    agent_output = execution.log_path.read_text(encoding="utf-8", errors="replace") if execution.log_path.exists() else execution.note
    append_turn(
        repo_root,
        instance=instance,
        conversation_id=conversation_id,
        task_id=task_id,
        prompt_text=prompt_text,
        agent_output=agent_output,
        log_path=execution.log_path,
    )


def run_quality_checks(repo_root: Path, task: dict[str, Any]) -> tuple[bool, list[str], str | None]:
    checks = task.get("quality_checks") or []
    log_paths: list[str] = []
    for index, check in enumerate(checks, start=1):
        task_id = str(task.get("id", "unknown"))
        log_path = repo_root / "logs" / f"{task_id}_check_{index}.log"
        if isinstance(check, str):
            command = shlex.split(check, posix=os.name != "nt")
        elif isinstance(check, list) and all(isinstance(part, str) for part in check):
            command = check
        else:
            return False, log_paths, f"unsupported quality check format at index {index}"

        command = normalize_quality_check_command(command)
        if not command:
            return False, log_paths, f"quality check command is not allowed: {' '.join(command)}"

        try:
            result = _run_capture(command, repo_root)
        except OSError as exc:
            append_text(log_path, str(exc))
            log_paths.append(str(log_path.relative_to(repo_root).as_posix()))
            return False, log_paths, f"could not start quality check: {' '.join(command)} ({exc})"

        append_text(log_path, result.stdout or "")
        log_paths.append(str(log_path.relative_to(repo_root).as_posix()))
        if result.returncode != 0:
            return False, log_paths, f"quality check failed: {' '.join(command)}"
    return True, log_paths, None


def normalize_quality_check_command(command: list[str]) -> list[str]:
    if not command:
        return []
    executable = Path(command[0]).name.lower()
    if executable in {"pytest", "pytest.exe"}:
        return [sys.executable, "-m", "pytest", *command[1:]]
    if executable in {"python", "python.exe", "python3", "python3.exe"} and len(command) >= 3 and command[1:3] == ["-m", "pytest"]:
        return [sys.executable, *command[1:]]
    return []


def is_allowed_quality_check(command: list[str]) -> bool:
    return bool(normalize_quality_check_command(command))


def _read_attempt_limits(task: dict[str, Any]) -> tuple[int | None, int | None, str | None]:
    try:
        attempts = int(task.get("attempts", 0))
        max_attempts = int(task.get("max_attempts", 3))
    except (TypeError, ValueError):
        return None, None, "attempts and max_attempts must be integers"
    if attempts < 0 or max_attempts < 1:
        return None, None, "attempts must be >= 0 and max_attempts must be >= 1"
    return attempts, max_attempts, None


def _save_task(repo_root: Path, queue: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    updated_queue = replace_task(queue, task)
    save_queue(repo_root, updated_queue)
    return updated_queue


def normalize_repo_path(path: str) -> str:
    return Path(path).as_posix().lstrip("./")


def collect_changed_files(repo_root: Path, before_files: set[str], extra_paths: list[str]) -> list[str]:
    changed_files = {normalize_repo_path(path) for path in before_files}
    if git_ops.is_git_repo(repo_root):
        changed_files.update(normalize_repo_path(path) for path in git_ops.changed_files(repo_root))
    changed_files.update(normalize_repo_path(path) for path in extra_paths if path)
    return sorted(changed_files)


def missing_expected_outputs(task: dict[str, Any], changed_files: list[str]) -> list[str]:
    expected_outputs = task.get("expected_outputs") or []
    changed = {normalize_repo_path(path) for path in changed_files}
    missing: list[str] = []
    for output in expected_outputs:
        if not isinstance(output, str):
            continue
        normalized = normalize_repo_path(output)
        if normalized not in changed:
            missing.append(normalized)
    return missing


def fail_running_task(
    repo_root: Path,
    queue: dict[str, Any],
    running_task: dict[str, Any],
    *,
    logs: list[str],
    changed_files: list[str],
    note: str,
    error: str,
) -> dict[str, Any]:
    task_id = str(running_task.get("id", "unknown"))
    orchestrator_log = task_orchestrator_log_path(repo_root, task_id)
    append_text(orchestrator_log, f"{utc_now_iso()} {error}")
    orchestrator_log_rel = str(orchestrator_log.relative_to(repo_root).as_posix())
    if orchestrator_log_rel not in logs:
        logs = [*logs, orchestrator_log_rel]

    failed = transition_task(
        running_task,
        FAILED,
        changed_files=changed_files,
        logs=logs,
        last_note=note,
        last_error=error,
        finished_at=utc_now_iso(),
    )
    _save_task(repo_root, queue, failed)
    append_progress(repo_root, f"Task {task_id} failed: {error}.")
    return {"executed": True, "status": FAILED, "task_id": task_id}


def run_one(repo_root: Path, runner_id: str = "local-runner", executor: TaskExecutor | None = None) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    executor = executor or default_task_executor
    queue = load_queue(repo_root)
    task = select_pending_task(queue["tasks"])

    if task is None:
        append_progress(repo_root, "No pending task found for local runner.")
        return {"executed": False, "status": "idle", "task_id": None}

    task_id = str(task.get("id", "unknown"))
    if task.get("requires_human_approval") or task.get("type") == "hardware_execution":
        blocked = transition_task(
            task,
            BLOCKED,
            last_note="Blocked because human approval is required before execution.",
            last_error=None,
            finished_at=utc_now_iso(),
        )
        _save_task(repo_root, queue, blocked)
        append_progress(repo_root, f"Task {task_id} blocked: human approval required.")
        return {"executed": False, "status": BLOCKED, "task_id": task_id}

    attempts, max_attempts, attempt_error = _read_attempt_limits(task)
    if attempt_error:
        failed = transition_task(
            task,
            FAILED,
            last_note="Task retry metadata is invalid.",
            last_error=attempt_error,
            finished_at=utc_now_iso(),
        )
        _save_task(repo_root, queue, failed)
        append_progress(repo_root, f"Task {task_id} failed without execution: {attempt_error}.")
        return {"executed": False, "status": FAILED, "task_id": task_id}

    assert attempts is not None
    assert max_attempts is not None
    if attempts >= max_attempts:
        failed = transition_task(
            task,
            FAILED,
            last_note="Task exceeded max_attempts and was not executed.",
            last_error=f"attempts {attempts} reached max_attempts {max_attempts}",
            finished_at=utc_now_iso(),
        )
        _save_task(repo_root, queue, failed)
        append_progress(repo_root, f"Task {task_id} failed without execution: max attempts reached.")
        return {"executed": False, "status": FAILED, "task_id": task_id}

    claimed = transition_task(task, CLAIMED, claimed_by=runner_id, claimed_at=utc_now_iso())
    queue = _save_task(repo_root, queue, claimed)
    append_progress(repo_root, f"Task {task_id} claimed by {runner_id}.")

    running = transition_task(claimed, RUNNING, started_at=utc_now_iso(), attempts=attempts + 1)
    queue = _save_task(repo_root, queue, running)
    append_progress(repo_root, f"Task {task_id} started.")

    before_files = set(git_ops.changed_files(repo_root)) if git_ops.is_git_repo(repo_root) else set()
    logs = list(running.get("logs", []))
    common_paths = ["tasks/task_queue.json", "progress.md"]
    if is_multi_turn_task(running):
        instance = codex_instance_from_task(running)
        conversation_id = conversation_id_from_task(running)
        if conversation_id:
            common_paths.append(str(transcript_path(repo_root, instance, conversation_id).relative_to(repo_root).as_posix()))
            common_paths.append(str(merged_prompt_path(repo_root, instance, conversation_id, task_id).relative_to(repo_root).as_posix()))
    try:
        execution = executor(repo_root, running)
        _record_multi_turn_if_needed(repo_root, running, execution)
        execution_log = str(execution.log_path.relative_to(repo_root).as_posix())
        logs.append(execution_log)
        common_paths.append(execution_log)

        if not execution.success:
            changed_files = collect_changed_files(repo_root, before_files, common_paths)
            return fail_running_task(
                repo_root,
                queue,
                running,
                logs=logs,
                changed_files=changed_files,
                note=execution.note,
                error=execution.error or execution.note,
            )

        checks_ok, check_logs, check_error = run_quality_checks(repo_root, running)
        logs.extend(check_logs)
        common_paths.extend(check_logs)
        changed_files = collect_changed_files(repo_root, before_files, common_paths)

        if not checks_ok:
            return fail_running_task(
                repo_root,
                queue,
                running,
                logs=logs,
                changed_files=changed_files,
                note="Quality checks failed.",
                error=check_error or "quality checks failed",
            )

        missing_outputs = missing_expected_outputs(running, changed_files)
        if missing_outputs:
            return fail_running_task(
                repo_root,
                queue,
                running,
                logs=logs,
                changed_files=changed_files,
                note="Expected outputs were not produced.",
                error=f"missing expected outputs: {', '.join(missing_outputs)}",
            )
    except Exception as exc:  # noqa: BLE001
        changed_files = collect_changed_files(repo_root, before_files, common_paths)
        return fail_running_task(
            repo_root,
            queue,
            running,
            logs=logs,
            changed_files=changed_files,
            note="Orchestrator raised an exception.",
            error=f"orchestrator exception: {exc}",
        )

    review = transition_task(
        running,
        REVIEW,
        changed_files=changed_files,
        logs=logs,
        last_note="Local execution completed; waiting for Hermes review.",
        last_error=None,
        finished_at=utc_now_iso(),
    )
    _save_task(repo_root, queue, review)
    append_progress(repo_root, f"Task {task_id} moved to review.")
    return {"executed": True, "status": REVIEW, "task_id": task_id}


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run one local orchestration pass.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    args = parser.parse_args(argv)
    result = run_one(Path(args.repo_root))
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
