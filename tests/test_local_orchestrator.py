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
