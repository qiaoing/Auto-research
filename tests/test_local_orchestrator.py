from pathlib import Path

from scripts import local_orchestrator


def test_resolve_cli_command_uses_windows_cmd_wrapper():
    command = local_orchestrator.resolve_cli_command("codex")

    assert Path(command).name == "codex.cmd"


def test_build_agent_command_uses_resolved_launcher():
    task = {
        "assigned_to": "codex",
        "prompt_file": "prompts/codex/SIM-001.md",
    }

    command = local_orchestrator.build_agent_command(task)

    assert Path(command[0]).name == "codex.cmd"
    assert command[1:3] == ["exec", "--full-auto"]


def test_expected_output_touched_returns_true_for_matching_files():
    task = {
        "expected_outputs": [
            "src/dynamics/underwater_vehicle.py",
            "tests/test_underwater_vehicle.py",
        ]
    }

    changed_files = [
        "progress.md",
        "src/dynamics/underwater_vehicle.py",
    ]

    assert local_orchestrator.expected_output_touched(task, changed_files)


def test_expected_output_touched_returns_false_for_non_matching_files():
    task = {
        "expected_outputs": [
            "src/dynamics/underwater_vehicle.py",
            "tests/test_underwater_vehicle.py",
        ]
    }

    changed_files = [
        "progress.md",
        "tasks/task_queue.json",
    ]

    assert not local_orchestrator.expected_output_touched(task, changed_files)
