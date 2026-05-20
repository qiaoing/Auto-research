from __future__ import annotations

import hashlib
import hmac
import os
import subprocess
import time
from pathlib import Path

from local_runner import orchestrator
from local_runner.locks import is_runner_busy, runner_lock_path
from local_runner.logging_utils import task_agent_log_path
from local_runner.orchestrator import TaskExecutionResult, _prompt_path, normalize_quality_check_command, run_one

from conftest import find_task, write_queue


def successful_executor(repo_root: Path, task: dict) -> TaskExecutionResult:
    log_path = task_agent_log_path(repo_root, task["id"])
    log_path.write_text("ok\n", encoding="utf-8")
    return TaskExecutionResult(True, log_path, "ok")


def test_task_id_cannot_escape_logs_directory(repo_root: Path) -> None:
    write_queue(
        repo_root,
        [
            {
                "id": "../escape",
                "title": "Unsafe id",
                "status": "pending",
            }
        ],
    )

    result = run_one(repo_root, executor=successful_executor)

    assert result["status"] == "review"
    assert not (repo_root / "escape_agent.log").exists()
    assert (repo_root / "logs" / "escape_agent.log").exists()
    assert find_task(repo_root, "../escape")["logs"] == ["logs/escape_agent.log"]


def test_prompt_file_must_stay_under_prompts(repo_root: Path) -> None:
    secret_path = repo_root / "secret.md"
    secret_path.write_text("secret", encoding="utf-8")
    prompt_path = repo_root / "prompts" / "codex" / "SIM-001.md"
    prompt_path.write_text("safe", encoding="utf-8")

    assert _prompt_path(repo_root, {"id": "SIM-001", "assigned_to": "codex"}) == prompt_path
    assert _prompt_path(repo_root, {"id": "SIM-001", "prompt_file": "../secret.md"}) is None
    assert _prompt_path(repo_root, {"id": "SIM-001", "prompt_file": str(secret_path)}) is None


def test_disallowed_quality_check_fails_without_running_command(repo_root: Path) -> None:
    marker = repo_root / "marker.txt"
    write_queue(
        repo_root,
        [
            {
                "id": "QC-001",
                "title": "Bad quality check",
                "status": "pending",
                "quality_checks": [["python", "-c", f"open({str(marker)!r}, 'w').write('bad')"]],
            }
        ],
    )

    result = run_one(repo_root, executor=successful_executor)

    assert result["status"] == "failed"
    assert not marker.exists()
    assert "not allowed" in find_task(repo_root, "QC-001")["last_error"]


def test_pytest_quality_check_is_normalized_to_python_module(repo_root: Path, monkeypatch) -> None:
    seen_commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        seen_commands.append(list(command))
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(orchestrator.subprocess, "run", fake_run)
    monkeypatch.setattr(orchestrator.git_ops, "is_git_repo", lambda _repo_root: False)

    write_queue(
        repo_root,
        [
            {
                "id": "QC-PYTEST",
                "title": "Normalize pytest",
                "status": "pending",
                "quality_checks": ["pytest tests/test_pid.py -q"],
            }
        ],
    )

    result = run_one(repo_root, executor=successful_executor)

    assert result["status"] == "review"
    assert seen_commands
    assert seen_commands[0][0].lower().endswith("python.exe") or seen_commands[0][0].lower().endswith("python")
    assert seen_commands[0][1:3] == ["-m", "pytest"]
    assert seen_commands[0][-1] == "-q"


def test_quality_check_launch_error_marks_task_failed(repo_root: Path, monkeypatch) -> None:
    def raising_run(command, **kwargs):
        raise FileNotFoundError("missing executable")

    monkeypatch.setattr(orchestrator.subprocess, "run", raising_run)
    monkeypatch.setattr(orchestrator.git_ops, "is_git_repo", lambda _repo_root: False)

    write_queue(
        repo_root,
        [
            {
                "id": "QC-MISSING",
                "title": "Missing quality executable",
                "status": "pending",
                "quality_checks": [["python", "-m", "pytest", "-q"]],
            }
        ],
    )

    result = run_one(repo_root, executor=successful_executor)

    assert result["status"] == "failed"
    task = find_task(repo_root, "QC-MISSING")
    assert task["status"] == "failed"
    assert "could not start quality check" in task["last_error"]
    assert task["finished_at"] is not None


def test_malformed_attempts_are_failed_without_execution(repo_root: Path) -> None:
    calls = []

    def executor(repo_root: Path, task: dict) -> TaskExecutionResult:
        calls.append(task["id"])
        return successful_executor(repo_root, task)

    write_queue(
        repo_root,
        [
            {
                "id": "BAD-ATTEMPTS",
                "title": "Bad attempts",
                "status": "pending",
                "attempts": "bad",
                "max_attempts": 3,
            }
        ],
    )

    result = run_one(repo_root, executor=executor)

    assert result["status"] == "failed"
    assert calls == []
    assert "must be integers" in find_task(repo_root, "BAD-ATTEMPTS")["last_error"]


def test_stale_lock_is_removed(repo_root: Path, monkeypatch) -> None:
    lock_path = runner_lock_path(repo_root)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("pid=1\n", encoding="utf-8")
    old_time = time.time() - 10
    os.utime(lock_path, (old_time, old_time))
    monkeypatch.setenv("LOCAL_RUNNER_LOCK_STALE_SECONDS", "1")

    assert is_runner_busy(repo_root) is False
    assert not lock_path.exists()


def test_logs_endpoint_does_not_return_service_log(client, repo_root: Path, auth_headers: dict[str, str]) -> None:
    service_log = repo_root / "logs" / "local_runner_service.log"
    service_log.write_text("internal service log\n", encoding="utf-8")

    response = client.get("/logs/local_runner_service", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["logs"] == []
    assert "internal service log" not in response.text


def test_irrelevant_github_webhook_push_is_ignored(client, monkeypatch) -> None:
    payload = b'{"commits":[{"added":["README.md"],"modified":[],"removed":[]}]}'
    digest = hmac.new(b"webhook-secret", payload, hashlib.sha256).hexdigest()
    headers = {
        "X-Hub-Signature-256": f"sha256={digest}",
        "X-GitHub-Event": "push",
    }
    calls = []

    def fake_launch(repo_root: Path) -> dict:
        calls.append(repo_root)
        return {"accepted": True}

    from local_runner import api_server

    monkeypatch.setattr(api_server, "launch_run_once", fake_launch)

    response = client.post("/webhook/github", content=payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["ignored"] is True
    assert calls == []
