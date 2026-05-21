# Multi-turn Codex Sessions

This runner supports both single-turn tasks and multi-turn Codex sessions.

## Task fields

Use these fields in `tasks/task_queue.json`:

- `assigned_to: "codex:<instance>"`  
  Example: `codex:planner`, `codex:controller`.
- `conversation_id`  
  Reuse the same value across turns in one logical session.
- `thread_id`  
  Optional alias field; if `conversation_id` is absent, `thread_id` is used.
- `multi_turn: true`  
  Optional explicit marker. If `conversation_id` is present, task is already multi-turn.
- `codex_instance` / `agent_instance`  
  Optional explicit instance override. If absent, parsed from `assigned_to`.

If task is `assigned_to: "codex"` and has no `conversation_id`/`thread_id`, it remains single-turn.

## Storage layout

Per-session data lives under:

`state/codex_sessions/<instance>/<conversation_id>/`

Files:

- `transcript.md`  
  Turn-by-turn conversation transcript.
- `metadata.json`  
  Includes turn list with `task_id`, `timestamp`, and `log_path`.
- `turns/<task_id>_merged_prompt.md`  
  Final merged prompt used for that turn (prior transcript + new prompt).

All `instance` and `conversation_id` components are sanitized to prevent path escape.

## Execution behavior

For multi-turn Codex task:

1. Load existing transcript (long transcript is truncated from the head, keeping the newest context).
2. Merge transcript + current prompt into one turn prompt.
3. Persist merged prompt to:
   `state/codex_sessions/<instance>/<conversation_id>/turns/<task_id>_merged_prompt.md`
4. Execute Codex.
5. Append this turn input/output to transcript and metadata.

If Codex execution fails, task becomes `failed`, but transcript and merged prompt are still kept for next repair turn.

## LOCAL_RUNNER_CODEX_COMMAND template

When `LOCAL_RUNNER_CODEX_COMMAND` is set, runner uses your template directly.

Supported placeholders include:

- `{task_id}`
- `{prompt_file}`
- `{merged_prompt_file}`
- `{conversation_id}`
- `{thread_id}`
- `{codex_instance}`
- `{agent_instance}`
- `{multi_turn}`
- `{repo_root}`
- `{log_file}`

Example:

```bash
LOCAL_RUNNER_CODEX_COMMAND="codex exec --cd {repo_root} --prompt-file {merged_prompt_file}"
```

If your Codex CLI has no `--prompt-file`, use a wrapper script that reads `{merged_prompt_file}` and forwards content.

## API visibility for Hermes

`GET /tasks` summary now includes:

- `conversation_id`
- `thread_id`
- `codex_instance`
- `agent_instance`
- `multi_turn`

This allows Hermes to track which pending/review/failed tasks belong to which local Codex session.

## Direct session API v2

The runner now also exposes protected conversation endpoints so cloud Hermes can append a live turn without creating a `tasks/task_queue.json` entry first:

- `POST /sessions`
- `GET /sessions/{conversation_id}?codex_instance=planner`
- `POST /sessions/{conversation_id}/turns`
- `GET /sessions/{conversation_id}/transcript?codex_instance=planner`

Example:

```bash
curl -sS -A 'Hermes-Agent/1.0' \
  -H "Authorization: Bearer $LOCAL_RUNNER_API_TOKEN" \
  -H 'Content-Type: application/json' \
  -X POST https://auto-runner.qiaoing.work/sessions \
  -d '{"conversation_id":"leaf-mpc-design","codex_instance":"planner"}'

curl -sS -A 'Hermes-Agent/1.0' \
  -H "Authorization: Bearer $LOCAL_RUNNER_API_TOKEN" \
  -H 'Content-Type: application/json' \
  -X POST https://auto-runner.qiaoing.work/sessions/leaf-mpc-design/turns \
  -d '{"codex_instance":"planner","turn_id":"turn-001","prompt":"继续上一轮 LEAF-MPC 架构设计，先列出要改的文件。"}'
```

The direct endpoint reuses the same Codex prompt merge and transcript persistence as task-queue mode. It stores inline prompts under `state/inline_prompts/`, merged prompts under `state/codex_sessions/<instance>/<conversation_id>/turns/`, and Codex output in the session transcript.

Security constraints:

- The API accepts prompt text and metadata only; it does not accept arbitrary shell commands.
- The same bearer token protects session endpoints.
- Path components are sanitized before writing session files.
- Hardware/approval policy remains enforced by task-queue mode; direct session turns should still be used only for software/research/code work.

## Current concurrency model

Runner is still single-process single-task serial execution by default.
Multi-instance here means logical session routing, not concurrent execution.
True parallel execution should be added later with isolated git worktrees per instance.

