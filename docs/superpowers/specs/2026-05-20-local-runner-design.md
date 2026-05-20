# Local Runner API Design

## Goal

Build a portable Windows/Linux local runner that lets Hermes query status and trigger fixed local execution through GitHub-backed tasks.

## Architecture

Core logic lives in `src/local_runner/`. Thin entry scripts in `scripts/` call package modules. GitHub remains the source of truth for tasks, prompts, logs, results, figures, and paper material.

## State Machine

Local execution supports `pending`, `claimed`, `running`, `review`, `done`, `failed`, `blocked`, and `cancelled`. The local runner only moves tasks through `pending -> claimed -> running -> review`, or to `failed`/`blocked` when safety or execution conditions require it.

## API

The FastAPI server provides `/health`, `/status`, `/tasks`, `/run-once`, `/logs/{task_id}`, and `/webhook/github`. `/health` is public. Status, task, run, and log endpoints require `LOCAL_RUNNER_API_TOKEN`. GitHub webhook requests require a valid `X-Hub-Signature-256` generated with `GITHUB_WEBHOOK_SECRET`.

## Safety

The API never accepts arbitrary shell commands or prompts. `/run-once` starts only the repository runner script. Tasks requiring human approval or hardware execution are blocked instead of executed. A lock file prevents concurrent runner passes.

## Deployment

Windows uses a PowerShell startup script or Task Scheduler. Linux uses a shell startup script or a user-level systemd service. Both platforms use the same Python package, scripts, environment variables, and repository task files.
