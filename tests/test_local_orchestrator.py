from local_runner.codex_sessions import (
    build_codex_prompt,
    codex_instance_from_task,
    conversation_id_from_task,
    is_multi_turn_task,
    transcript_path,
)
from local_runner.orchestrator import is_allowed_quality_check, select_pending_task
from local_runner.security import safe_filename_component


def test_select_pending_task_uses_priority_order():
    task = select_pending_task(
        [
            {"id": "B", "status": "pending", "priority": 2},
            {"id": "A", "status": "pending", "priority": 1},
            {"id": "DONE", "status": "done", "priority": 0},
        ]
    )

    assert task["id"] == "A"


def test_quality_check_policy_allows_pytest_forms():
    assert is_allowed_quality_check(["pytest", "-q"])
    assert is_allowed_quality_check(["python", "-m", "pytest", "-q"])
    assert not is_allowed_quality_check(["python", "-c", "print('unsafe')"])


def test_safe_filename_component_removes_path_separators():
    assert safe_filename_component("../SIM-001") == "SIM-001"


def test_codex_instance_and_conversation_can_be_declared_explicitly():
    task = {"assigned_to": "codex:planner", "conversation_id": "rl/mpc-thread"}

    assert codex_instance_from_task(task) == "planner"
    assert conversation_id_from_task(task) == "rl_mpc-thread"
    assert is_multi_turn_task(task)


def test_multi_turn_prompt_includes_prior_transcript(repo_root):
    path = transcript_path(repo_root, "planner", "ctrl-thread")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("## Turn T1\nPrevious decision: use pytest.\n", encoding="utf-8")

    prompt = build_codex_prompt(
        repo_root,
        {"assigned_to": "codex:planner", "conversation_id": "ctrl-thread"},
        "Continue with controller tests.",
    )

    assert "Previous decision: use pytest." in prompt
    assert "Continue with controller tests." in prompt
    assert "local Codex instance `planner`" in prompt
