# Local Runner API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a portable local runner API for Hermes-triggered Codex/OpenCode task execution.

**Architecture:** Keep task storage, state machine, runner service, API, git operations, locks, and logging in small Python modules under `src/local_runner/`. Expose only thin scripts under `scripts/`.

**Tech Stack:** Python 3.10+, FastAPI, uvicorn, pytest, Git CLI.

---

### Task 1: Repository Skeleton

**Files:**
- Create: `AGENTS.md`, `README.md`, `pyproject.toml`, `requirements.txt`, `tasks/task_queue.json`, `progress.md`
- Create: `prompts/`, `logs/`, `results/`, `figures/`, `paper/`

- [x] Create a portable Python project skeleton.
- [x] Add initial task queue schema and progress log.

### Task 2: State Machine And Orchestrator

**Files:**
- Create: `src/local_runner/state_machine.py`
- Create: `src/local_runner/task_store.py`
- Create: `src/local_runner/orchestrator.py`
- Create: `scripts/local_orchestrator.py`

- [x] Normalize old and new task queues.
- [x] Enforce local transitions and retry limits.
- [x] Block hardware or human-approval tasks.
- [x] Mark successful local work as `review`.

### Task 3: Runner Service

**Files:**
- Create: `src/local_runner/runner_service.py`
- Create: `src/local_runner/locks.py`
- Create: `src/local_runner/git_ops.py`
- Create: `scripts/local_runner_service.py`

- [x] Add `--once` and `--interval` modes.
- [x] Add lock-file concurrency protection.
- [x] Add pull, orchestrator, add, commit, push flow.
- [x] Add service log and status file.

### Task 4: API And Webhook

**Files:**
- Create: `src/local_runner/api_server.py`
- Create: `src/local_runner/api.py`
- Create: `scripts/local_runner_server.py`

- [x] Add `/health`, `/status`, `/tasks`, `/run-once`, `/logs/{task_id}`.
- [x] Add bearer token auth for protected endpoints.
- [x] Add signed GitHub push webhook with path filtering.

### Task 5: Deployment Docs And Scripts

**Files:**
- Create: `scripts/run_local_runner_server.sh`
- Create: `scripts/run_local_runner_server.ps1`
- Create: `scripts/install_local_runner_systemd.sh`
- Create: `docs/architecture.md`
- Create: `docs/runner_setup.md`

- [x] Document Windows and Linux startup.
- [x] Document token and webhook secret setup.
- [x] Document tunnel and GitHub webhook configuration.

### Task 6: Tests

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_public_behavior.py`

- [x] Cover state machine, human approval block, retry exhaustion, API auth, status counts, busy runner, webhook signature, relevant webhook trigger, and log traversal defense.
- [x] Run `python -m pytest -q`.
