from __future__ import annotations

import hashlib
import hmac
from types import SimpleNamespace
from pathlib import Path

from local_runner import runner_service
from local_runner import api_server
from local_runner.codex_sessions import merged_prompt_path, transcript_path
from local_runner.locks import runner_lock_path
from local_runner.orchestrator import TaskExecutionResult, run_one
from local_runner.state_machine import BLOCKED, FAILED, REVIEW

from conftest import find_task, write_queue


def successful_executor(repo_root: Path, task: dict) -> TaskExecutionResult:
    log_path = repo_root / "logs" / f"{task['id']}_agent.log"
    log_path.write_text("ok\n", encoding="utf-8")
    return TaskExecutionResult(True, log_path, "ok")


def test_task_state_machine_claim_run_review(repo_root: Path) -> None:
    write_queue(
        repo_root,
        [
            {
                "id": "SIM-001",
                "title": "Run simulation",
                "status": "pending",
                "attempts": 0,
                "max_attempts": 3,
            }
        ],
    )

    result = run_one(repo_root, executor=successful_executor)

    assert result["status"] == REVIEW
    task = find_task(repo_root, "SIM-001")
    assert task["status"] == "review"
    assert task["claimed_by"] == "local-runner"
    assert task["claimed_at"]
    assert task["started_at"]
    assert task["finished_at"]
    assert task["attempts"] == 1
    assert task["logs"] == ["logs/SIM-001_agent.log"]
    assert task["changed_files"]


def test_multi_turn_codex_task_records_transcript(repo_root: Path) -> None:
    write_queue(
        repo_root,
        [
            {
                "id": "THREAD-001",
                "title": "First turn",
                "assigned_to": "codex:planner",
                "conversation_id": "ctrl-thread",
                "status": "pending",
            }
        ],
    )

    result = run_one(repo_root, executor=successful_executor)

    assert result["status"] == REVIEW
    path = transcript_path(repo_root, "planner", "ctrl-thread")
    assert path.exists()
    transcript = path.read_text(encoding="utf-8")
    assert "Turn THREAD-001" in transcript
    assert "First turn" in transcript
    task = find_task(repo_root, "THREAD-001")
    assert "state/codex_sessions/planner/ctrl-thread/transcript.md" in task["changed_files"]


def test_second_turn_merged_prompt_includes_first_turn_transcript(repo_root: Path, monkeypatch) -> None:
    prompt_dir = repo_root / "prompts" / "codex"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "TURN-1.md").write_text("First turn prompt.", encoding="utf-8")
    (prompt_dir / "TURN-2.md").write_text("Second turn prompt.", encoding="utf-8")
    write_queue(
        repo_root,
        [
            {
                "id": "TURN-1",
                "title": "First turn",
                "assigned_to": "codex:planner",
                "conversation_id": "ctrl-thread",
                "status": "pending",
                "prompt_file": "prompts/codex/TURN-1.md",
                "expected_outputs": [],
                "quality_checks": [],
            },
            {
                "id": "TURN-2",
                "title": "Second turn",
                "assigned_to": "codex:planner",
                "conversation_id": "ctrl-thread",
                "status": "pending",
                "prompt_file": "prompts/codex/TURN-2.md",
                "expected_outputs": [],
                "quality_checks": [],
            },
        ],
    )

    captured: list[tuple[list[str], str | None]] = []
    monkeypatch.setattr("local_runner.orchestrator.shutil.which", lambda _name: "codex")

    def fake_run_capture(command, _repo_root, input_text=None):
        captured.append((command, input_text))
        return SimpleNamespace(returncode=0, stdout="ok")

    monkeypatch.setattr("local_runner.orchestrator._run_capture", fake_run_capture)

    first = run_one(repo_root)
    second = run_one(repo_root)

    assert first["status"] == REVIEW
    assert second["status"] == REVIEW
    assert len(captured) == 2
    assert captured[0][0][-1] == "-"
    assert captured[1][0][-1] == "-"
    assert "First turn prompt." in (captured[0][1] or "")
    assert "Turn TURN-1" in (captured[1][1] or "")
    assert "Second turn prompt." in (captured[1][1] or "")


def test_requires_human_approval_becomes_blocked_without_execution(repo_root: Path) -> None:
    calls = []

    def executor(repo_root: Path, task: dict) -> TaskExecutionResult:
        calls.append(task["id"])
        return successful_executor(repo_root, task)

    write_queue(
        repo_root,
        [
            {
                "id": "HW-001",
                "title": "Hardware test",
                "status": "pending",
                "requires_human_approval": True,
            }
        ],
    )

    result = run_one(repo_root, executor=executor)

    assert result["status"] == BLOCKED
    assert calls == []
    assert find_task(repo_root, "HW-001")["status"] == "blocked"


def test_attempts_at_max_attempts_is_marked_failed_without_execution(repo_root: Path) -> None:
    calls = []

    def executor(repo_root: Path, task: dict) -> TaskExecutionResult:
        calls.append(task["id"])
        return successful_executor(repo_root, task)

    write_queue(
        repo_root,
        [
            {
                "id": "SIM-RETRY",
                "title": "Retry exhausted",
                "status": "pending",
                "attempts": 3,
                "max_attempts": 3,
            }
        ],
    )

    result = run_one(repo_root, executor=executor)

    assert result["status"] == FAILED
    assert calls == []
    task = find_task(repo_root, "SIM-RETRY")
    assert task["status"] == "failed"
    assert "max_attempts" in task["last_error"]


def test_agent_failure_marks_running_task_failed(repo_root: Path) -> None:
    def failing_executor(repo_root: Path, task: dict) -> TaskExecutionResult:
        log_path = repo_root / "logs" / f"{task['id']}_agent.log"
        log_path.write_text("failed\n", encoding="utf-8")
        return TaskExecutionResult(False, log_path, "agent execution failed", "simulated failure")

    write_queue(
        repo_root,
        [
            {
                "id": "SIM-FAIL",
                "title": "Failing task",
                "status": "pending",
                "attempts": 0,
                "max_attempts": 3,
            }
        ],
    )

    result = run_one(repo_root, executor=failing_executor)

    assert result["status"] == FAILED
    task = find_task(repo_root, "SIM-FAIL")
    assert task["status"] == "failed"
    assert task["finished_at"] is not None
    assert task["last_error"] == "simulated failure"
    assert task["logs"] == ["logs/SIM-FAIL_agent.log", "logs/SIM-FAIL_orchestrator.log"]


def test_multi_turn_failure_keeps_transcript_and_merged_prompt(repo_root: Path, monkeypatch) -> None:
    prompt_dir = repo_root / "prompts" / "codex"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "TURN-FAIL.md").write_text("Fail this turn.", encoding="utf-8")
    write_queue(
        repo_root,
        [
            {
                "id": "TURN-FAIL",
                "title": "Failing multi-turn",
                "assigned_to": "codex:planner",
                "conversation_id": "ctrl-thread",
                "status": "pending",
                "prompt_file": "prompts/codex/TURN-FAIL.md",
            }
        ],
    )

    monkeypatch.setattr("local_runner.orchestrator.shutil.which", lambda _name: "codex")
    monkeypatch.setattr(
        "local_runner.orchestrator._run_capture",
        lambda _command, _repo_root, input_text=None: SimpleNamespace(returncode=7, stdout="execution failed"),
    )

    result = run_one(repo_root)
    assert result["status"] == FAILED

    task = find_task(repo_root, "TURN-FAIL")
    assert task["status"] == "failed"
    tpath = transcript_path(repo_root, "planner", "ctrl-thread")
    assert tpath.exists()
    assert "Turn TURN-FAIL" in tpath.read_text(encoding="utf-8", errors="replace")
    mpath = merged_prompt_path(repo_root, "planner", "ctrl-thread", "TURN-FAIL")
    assert mpath.exists()


def test_service_still_attempts_publish_when_orchestrator_raises(repo_root: Path, monkeypatch) -> None:
    calls: list[str] = []

    def fake_run_one(repo_root: Path, runner_id: str = "local-runner"):
        (repo_root / "progress.md").write_text("# Progress\n- changed\n", encoding="utf-8")
        raise RuntimeError("boom")

    def record_call(name: str):
        def inner(*args, **kwargs):
            calls.append(name)
            return None
        return inner

    monkeypatch.setattr(runner_service, "run_one", fake_run_one)
    monkeypatch.setattr(runner_service.git_ops, "pull_rebase", record_call("pull"))
    monkeypatch.setattr(runner_service.git_ops, "add_all", record_call("add"))
    monkeypatch.setattr(runner_service.git_ops, "commit", record_call("commit"))
    monkeypatch.setattr(runner_service.git_ops, "push", record_call("push"))

    result = runner_service.run_once(repo_root, run_id="test-run")

    assert result["status"] == "error"
    assert calls == ["pull", "add", "commit", "push"]


def test_service_pulls_before_writing_running_status(repo_root: Path, monkeypatch) -> None:
    calls: list[str] = []

    def fake_pull(_repo_root: Path):
        calls.append("pull")
        return None

    def fake_status(_repo_root: Path, **updates):
        if updates.get("last_run_status") == "running":
            calls.append("status-running")
        return {}

    monkeypatch.setattr(runner_service.git_ops, "pull_rebase", fake_pull)
    monkeypatch.setattr(runner_service, "write_runner_status", fake_status)
    monkeypatch.setattr(runner_service, "run_one", lambda _repo_root, runner_id="local-runner": {"status": "idle", "task_id": None})
    monkeypatch.setattr(runner_service.git_ops, "add_all", lambda _repo_root: None)
    monkeypatch.setattr(runner_service.git_ops, "commit", lambda _repo_root, _message: None)
    monkeypatch.setattr(runner_service.git_ops, "push", lambda _repo_root: None)

    runner_service.run_once(repo_root, run_id="ordering-test")

    assert calls[:2] == ["pull", "status-running"]


def test_service_retries_push_after_fetch_first_rejection(repo_root: Path, monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(runner_service, "run_one", lambda _repo_root, runner_id="local-runner": {"status": "idle", "task_id": None})
    monkeypatch.setattr(runner_service, "write_runner_status", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(runner_service.git_ops, "add_all", lambda _repo_root: None)
    monkeypatch.setattr(runner_service.git_ops, "commit", lambda _repo_root, _message: None)
    monkeypatch.setattr(runner_service.git_ops, "pull_rebase", lambda _repo_root: calls.append("pull") or None)

    responses = [
        SimpleNamespace(returncode=1, stdout="! [rejected] main -> main (fetch first)"),
        SimpleNamespace(returncode=0, stdout="pushed"),
    ]

    def fake_push(_repo_root: Path):
        calls.append("push")
        return responses.pop(0)

    monkeypatch.setattr(runner_service.git_ops, "push", fake_push)

    runner_service.run_once(repo_root, run_id="push-retry-test")

    assert calls == ["pull", "push", "pull", "push"]


def test_health_returns_ok(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_status_returns_task_counts(client, repo_root: Path, auth_headers: dict[str, str]) -> None:
    write_queue(
        repo_root,
        [
            {"id": "pending-1", "title": "A", "status": "pending"},
            {"id": "pending-2", "title": "B", "status": "pending"},
            {"id": "running-1", "title": "C", "status": "running"},
            {"id": "review-1", "title": "D", "status": "review"},
            {"id": "blocked-1", "title": "E", "status": "blocked"},
        ],
    )

    response = client.get("/status", headers=auth_headers)

    assert response.status_code == 200
    counts = response.json()["tasks"]
    assert counts["pending"] == 2
    assert counts["running"] == 1
    assert counts["review"] == 1
    assert counts["blocked"] == 1


def test_status_includes_changed_files_when_git_dirty(client, repo_root: Path, auth_headers: dict[str, str], monkeypatch) -> None:
    monkeypatch.setattr(api_server.git_ops, "is_git_repo", lambda _repo_root: True)
    monkeypatch.setattr(api_server.git_ops, "is_dirty", lambda _repo_root: True)
    monkeypatch.setattr(api_server.git_ops, "changed_files", lambda _repo_root: ["tasks/task_queue.json", "progress.md"])
    monkeypatch.setattr(api_server.git_ops, "current_branch", lambda _repo_root: "main")
    monkeypatch.setattr(api_server.git_ops, "current_head", lambda _repo_root: "abc1234")

    response = client.get("/status", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["git"]["changed_files"] == ["tasks/task_queue.json", "progress.md"]


def test_tasks_summary_includes_multi_turn_fields(client, repo_root: Path, auth_headers: dict[str, str]) -> None:
    write_queue(
        repo_root,
        [
            {
                "id": "R-1",
                "title": "Research turn",
                "assigned_to": "codex:planner",
                "conversation_id": "ctrl-thread",
                "multi_turn": True,
                "status": "pending",
            }
        ],
    )

    response = client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200
    task = response.json()["tasks"][0]
    assert task["conversation_id"] == "ctrl-thread"
    assert task["codex_instance"] == "planner"
    assert task["multi_turn"] is True


def test_custom_codex_template_receives_merged_prompt_file(repo_root: Path, monkeypatch) -> None:
    prompt_dir = repo_root / "prompts" / "codex"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "TPL-001.md").write_text("template turn", encoding="utf-8")
    write_queue(
        repo_root,
        [
            {
                "id": "TPL-001",
                "title": "Template turn",
                "assigned_to": "codex:planner",
                "conversation_id": "ctrl-thread",
                "status": "pending",
                "prompt_file": "prompts/codex/TPL-001.md",
            }
        ],
    )

    captured: list[list[str]] = []
    monkeypatch.setenv(
        "LOCAL_RUNNER_CODEX_COMMAND",
        "custom-codex --merged {merged_prompt_file} --conversation {conversation_id} --instance {codex_instance}",
    )
    monkeypatch.setattr(
        "local_runner.orchestrator._run_capture",
        lambda command, _repo_root, input_text=None: captured.append(command) or SimpleNamespace(returncode=0, stdout="ok"),
    )

    result = run_one(repo_root)
    assert result["status"] == REVIEW
    assert captured
    assert "custom-codex" in captured[0][0]
    merged = merged_prompt_path(repo_root, "planner", "ctrl-thread", "TPL-001")
    assert merged.exists()
    assert str(merged) in " ".join(captured[0])
    content = merged.read_text(encoding="utf-8")
    assert "template turn" in content


def test_single_turn_codex_task_does_not_create_session_files(repo_root: Path, monkeypatch) -> None:
    prompt_dir = repo_root / "prompts" / "codex"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "SINGLE-001.md").write_text("single turn", encoding="utf-8")
    write_queue(
        repo_root,
        [
            {
                "id": "SINGLE-001",
                "title": "Single turn",
                "assigned_to": "codex",
                "status": "pending",
                "prompt_file": "prompts/codex/SINGLE-001.md",
            }
        ],
    )
    monkeypatch.setattr("local_runner.orchestrator.shutil.which", lambda _name: "codex")
    captured: list[tuple[list[str], str | None]] = []
    monkeypatch.setattr(
        "local_runner.orchestrator._run_capture",
        lambda _command, _repo_root, input_text=None: captured.append((_command, input_text)) or SimpleNamespace(returncode=0, stdout="ok"),
    )

    result = run_one(repo_root)
    assert result["status"] == REVIEW
    assert captured and captured[0][0][-1] == "-"
    assert "single turn" in (captured[0][1] or "")
    assert not (repo_root / "state" / "codex_sessions").exists()


def test_run_once_returns_busy_when_runner_lock_exists(client, repo_root: Path, auth_headers: dict[str, str]) -> None:
    lock_path = runner_lock_path(repo_root)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("busy\n", encoding="utf-8")

    response = client.post("/run-once", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "accepted": False,
        "busy": True,
        "message": "runner is already running",
    }


def test_protected_apis_return_401_without_authorization(client) -> None:
    for method, path in (("get", "/status"), ("post", "/run-once"), ("get", "/logs/SIM-001")):
        response = getattr(client, method)(path)
        assert response.status_code == 401


def test_bad_github_webhook_signature_returns_401(client) -> None:
    payload = b'{"commits":[]}'
    headers = {
        "X-Hub-Signature-256": "sha256=bad",
        "X-GitHub-Event": "push",
    }

    response = client.post("/webhook/github", content=payload, headers=headers)

    assert response.status_code == 401


def test_github_webhook_triggers_run_once_for_relevant_push(client, monkeypatch) -> None:
    payload = b'{"commits":[{"added":["tasks/task_queue.json"],"modified":[],"removed":[]}]}'
    digest = hmac.new(b"webhook-secret", payload, hashlib.sha256).hexdigest()
    headers = {
        "X-Hub-Signature-256": f"sha256={digest}",
        "X-GitHub-Event": "push",
    }
    calls = []

    def fake_launch(repo_root: Path) -> dict:
        calls.append(repo_root)
        return {"accepted": True, "busy": False, "message": "runner started", "run_id": "test"}

    monkeypatch.setattr(api_server, "launch_run_once", fake_launch)

    response = client.post("/webhook/github", content=payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert len(calls) == 1


def test_logs_rejects_path_traversal(client, repo_root: Path, auth_headers: dict[str, str]) -> None:
    outside = repo_root / "secret.log"
    outside.write_text("do not expose", encoding="utf-8")

    response = client.get("/logs/%2E%2E%2Fsecret", headers=auth_headers)

    assert response.status_code in {400, 404, 422}
    assert "do not expose" not in response.text


def test_logs_include_orchestrator_log(client, repo_root: Path, auth_headers: dict[str, str]) -> None:
    (repo_root / "logs" / "SIM-ERR_orchestrator.log").write_text("orchestrator failure\n", encoding="utf-8")

    response = client.get("/logs/SIM-ERR", headers=auth_headers)

    assert response.status_code == 200
    files = [entry["file"] for entry in response.json()["logs"]]
    assert "orchestrator failure" in response.text
    assert any(path.endswith("SIM-ERR_orchestrator.log") for path in files)
