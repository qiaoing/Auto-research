from pathlib import Path
from types import SimpleNamespace

from local_runner.session_worker import append_session_turn, build_inline_prompt_for_tests, read_session_transcript


def test_append_session_turn_reuses_transcript_context(repo_root: Path, monkeypatch) -> None:
    captured: list[str | None] = []
    monkeypatch.setattr("local_runner.orchestrator.shutil.which", lambda _name: "codex")

    def fake_run_capture(_command, _repo_root, input_text=None):
        captured.append(input_text)
        return SimpleNamespace(returncode=0, stdout="codex output ok")

    monkeypatch.setattr("local_runner.orchestrator._run_capture", fake_run_capture)

    first = append_session_turn(
        repo_root,
        conversation_id="direct-chat",
        codex_instance="planner",
        turn_id="turn-1",
        prompt="First live prompt marker ABC123.",
    )
    second = append_session_turn(
        repo_root,
        conversation_id="direct-chat",
        codex_instance="planner",
        turn_id="turn-2",
        prompt="Can you see the marker?",
    )

    assert first.success is True
    assert second.success is True
    assert len(captured) == 2
    assert "First live prompt marker ABC123." in (captured[0] or "")
    assert "Turn turn-1" in (captured[1] or "")
    assert "First live prompt marker ABC123." in (captured[1] or "")
    transcript = read_session_transcript(repo_root, "direct-chat", "planner")["transcript"]
    assert "Turn turn-1" in transcript
    assert "Turn turn-2" in transcript


def test_session_api_two_turn_roundtrip(client, repo_root: Path, auth_headers: dict[str, str], monkeypatch) -> None:
    monkeypatch.setattr("local_runner.session_worker.default_task_executor", None, raising=False)

    def fake_executor(repo_root: Path, task: dict):
        log_path = repo_root / "logs" / f"{task['id']}_agent.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        prompt = build_inline_prompt_for_tests(repo_root, task["conversation_id"], task["inline_prompt"], task["codex_instance"])
        log_path.write_text(f"FAKE CODEX SAW:\n{prompt}\n", encoding="utf-8")
        from local_runner.orchestrator import TaskExecutionResult
        return TaskExecutionResult(True, log_path, "fake ok")

    monkeypatch.setattr("local_runner.api_server.append_session_turn", lambda *args, **kwargs: append_session_turn(*args, **kwargs, executor=fake_executor))

    create = client.post("/sessions", headers=auth_headers, json={"conversation_id": "api-chat", "codex_instance": "planner"})
    assert create.status_code == 200
    assert create.json()["session"]["conversation_id"] == "api-chat"

    first = client.post(
        "/sessions/api-chat/turns",
        headers=auth_headers,
        json={"codex_instance": "planner", "turn_id": "api-1", "prompt": "First API prompt marker XYZ789."},
    )
    assert first.status_code == 200
    assert first.json()["turn"]["status"] == "review"

    second = client.post(
        "/sessions/api-chat/turns",
        headers=auth_headers,
        json={"codex_instance": "planner", "turn_id": "api-2", "prompt": "Do you remember the marker?"},
    )
    assert second.status_code == 200
    transcript = client.get("/sessions/api-chat/transcript?codex_instance=planner", headers=auth_headers)
    assert transcript.status_code == 200
    text = transcript.json()["transcript"]
    assert "First API prompt marker XYZ789." in text
    assert "Turn api-2" in text
