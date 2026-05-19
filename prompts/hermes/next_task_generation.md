# Hermes Next Task Generation Template

## Purpose

Generate the next actionable local tasks for Codex or OpenCode based on repository state and research priorities.

## Inputs

- current queue in `tasks/task_queue.json`
- completed items in `tasks/completed_tasks.json`
- current stage in `project_state.json`
- latest notes in `progress.md`

## Constraints

- Prefer small, testable, repository-local tasks
- Separate coding, plotting, paper, and research-analysis work
- Do not generate automatic hardware execution tasks
- Mark any hardware-adjacent work as design-only unless a human explicitly approves execution

## Output Requirements

For each new task, provide:

- `id`
- `title`
- `type`
- `assigned_to`
- `priority`
- `status`
- `prompt_file`
- `expected_outputs`
- `quality_checks`
- `requires_human_approval`

## Heuristics

- Prioritize simulation enablers first
- Ensure at least one baseline and one plotting task are available
- Keep paper tasks aligned with actual completed results
