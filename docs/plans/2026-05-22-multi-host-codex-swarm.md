# Multi-Host Codex Swarm Coordination Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Enable one cloud Hermes orchestrator to maintain continuous multi-turn conversations with Codex workers running on multiple different computers, and coordinate them on complex research/software tasks.

**Architecture:** Introduce a cloud-side worker registry and router. Each local computer exposes the existing protected session API (`/sessions`, `/sessions/{conversation_id}/turns`, `/sessions/{conversation_id}/transcript`) under its own endpoint. Cloud Hermes addresses work by `worker_id + conversation_id`, not by a single global runner URL. Git remains the durable artifact/audit layer, while HTTP handles live turns.

**Tech Stack:** Python, FastAPI local runners, JSON/YAML worker registry, Cloudflare Tunnel/Tailscale/ngrok per host, bearer tokens per worker, Git for artifact persistence.

---

## Target Architecture

```text
                         Feishu / User
                              │
                              ▼
                    Cloud Hermes Orchestrator
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
   Worker Registry     Session Router      Task/Plan State
            │                 │                 │
            ├──── worker_id=desktop-gpu ────────┐
            │                                    ▼
            │                         https://desktop-runner.../
            │                                    │
            │                                    ▼
            │                         Local Codex / GPU / repo
            │
            ├──── worker_id=laptop-win ─────────┐
            │                                    ▼
            │                         https://laptop-runner.../
            │                                    │
            │                                    ▼
            │                         Local Codex / Windows tools
            │
            └──── worker_id=lab-ros ────────────┐
                                                 ▼
                                      https://lab-runner.../
                                                 │
                                                 ▼
                                      Local Codex / ROS / hardware dry-run
```

---

## Core Concepts

### Worker

A worker is one reachable local runner installation, usually one computer.

Minimum fields:

```json
{
  "worker_id": "desktop-gpu",
  "label": "Desktop GPU workstation",
  "base_url": "https://desktop-runner.example.com",
  "token_env": "LOCAL_RUNNER_DESKTOP_GPU_TOKEN",
  "capabilities": ["python", "cuda", "codex", "simulation"],
  "repo": "Auto-research",
  "status": "active",
  "max_concurrent_sessions": 1
}
```

### Session

A session is scoped by both worker and conversation:

```text
worker_id: desktop-gpu
conversation_id: leaf-mpc-sim
codex_instance: planner
```

Do not rely on `conversation_id` alone globally, because two different computers may both have `leaf-mpc-sim`.

### Turn

A turn is one Hermes → Codex follow-up. Routing key:

```text
worker_id + conversation_id + codex_instance + turn_id
```

---

## Task 1: Add a Cloud-Side Worker Registry

**Objective:** Store the list of reachable local Codex workers without hard-coding one `auto-runner.qiaoing.work` endpoint.

**Files:**
- Create: `config/worker_registry.example.json`
- Create: `src/cloud_orchestrator/worker_registry.py`
- Test: `tests/test_worker_registry.py`

**Step 1: Create example registry**

```json
{
  "schema_version": 1,
  "workers": [
    {
      "worker_id": "desktop-gpu",
      "label": "Desktop GPU workstation",
      "base_url": "https://desktop-runner.example.com",
      "token_env": "LOCAL_RUNNER_DESKTOP_GPU_TOKEN",
      "capabilities": ["codex", "python", "cuda", "simulation"],
      "repo": "Auto-research",
      "status": "active",
      "max_concurrent_sessions": 1
    }
  ]
}
```

**Step 2: Implement loader**

`worker_registry.py` should:
- load JSON from `LOCAL_CODEX_WORKER_REGISTRY` or default `config/worker_registry.json`;
- validate unique `worker_id`;
- never store bearer token values in the registry, only `token_env` names;
- expose `get_worker(worker_id)` and `list_workers(capability=None)`.

**Step 3: Tests**

Verify:
- duplicate worker IDs fail;
- inactive workers are excluded by default;
- token values are resolved from environment only at request time.

---

## Task 2: Add a Cloud-Side Session Router

**Objective:** Provide one API/client function that sends a turn to the correct computer.

**Files:**
- Create: `src/cloud_orchestrator/session_router.py`
- Test: `tests/test_session_router.py`

**Step 1: Implement client functions**

Functions:

```python
create_session(worker_id, conversation_id, codex_instance="default")
append_turn(worker_id, conversation_id, prompt, codex_instance="default", turn_id=None)
get_transcript(worker_id, conversation_id, codex_instance="default")
get_worker_status(worker_id)
```

**Step 2: HTTP behavior**

For each request:
- set `Authorization: Bearer <token from token_env>`;
- set `User-Agent: Hermes-Agent/1.0`;
- use timeout;
- return structured JSON with `worker_id`, `conversation_id`, `status`, `turn_id`, `error`.

**Step 3: Tests**

Mock HTTP calls and verify:
- URL route is correct;
- token env is used but not printed;
- missing worker/token gives clear error;
- non-2xx response is captured as failed turn.

---

## Task 3: Add Multi-Worker Orchestration State

**Objective:** Let Hermes remember which worker owns which sub-conversation in a complex project.

**Files:**
- Create: `state/cloud_sessions/index.json` or `state/orchestrator_sessions.json`
- Create: `src/cloud_orchestrator/session_index.py`
- Test: `tests/test_session_index.py`

**State format:**

```json
{
  "schema_version": 1,
  "projects": {
    "leaf-mpc-paper": {
      "sessions": [
        {
          "role": "simulation",
          "worker_id": "desktop-gpu",
          "conversation_id": "leaf-mpc-sim",
          "codex_instance": "sim",
          "status": "active",
          "last_turn_id": "sim-003"
        },
        {
          "role": "paper-writing",
          "worker_id": "laptop-win",
          "conversation_id": "leaf-mpc-paper",
          "codex_instance": "writer",
          "status": "active",
          "last_turn_id": "paper-002"
        }
      ]
    }
  }
}
```

**Step 1:** Implement lookup by project + role.

**Step 2:** Implement update after each turn.

**Step 3:** Record last result summary for routing decisions.

---

## Task 4: Add Fan-Out / Gather Coordination Helpers

**Objective:** Allow Hermes to ask several computers to work in parallel, then gather outputs and cross-feed results.

**Files:**
- Create: `src/cloud_orchestrator/swarm.py`
- Test: `tests/test_swarm.py`

**Functions:**

```python
fanout_turn(turns: list[TurnRequest]) -> list[TurnResult]
gather_transcripts(session_refs: list[SessionRef]) -> dict[str, str]
relay_context(source_ref, target_ref, instruction)
```

**Example workflow:**

1. Send simulation task to `desktop-gpu`.
2. Send literature synthesis task to `laptop-win`.
3. Gather both transcripts.
4. Send summary from both to `paper-writer` session.
5. Ask `reviewer` worker to critique the merged result.

---

## Task 5: Extend Local Runner Status for Capabilities

**Objective:** Let each local computer advertise what it can do.

**Files:**
- Modify: `src/local_runner/config.py`
- Modify: `src/local_runner/api_server.py`
- Test: `tests/test_public_behavior.py`

**New local env vars:**

```bash
LOCAL_RUNNER_WORKER_ID=desktop-gpu
LOCAL_RUNNER_LABEL="Desktop GPU workstation"
LOCAL_RUNNER_CAPABILITIES=codex,python,cuda,simulation
LOCAL_RUNNER_MAX_CONCURRENT_SESSIONS=1
```

**`GET /status` should include:**

```json
{
  "worker": {
    "worker_id": "desktop-gpu",
    "label": "Desktop GPU workstation",
    "capabilities": ["codex", "python", "cuda", "simulation"],
    "max_concurrent_sessions": 1
  }
}
```

---

## Task 6: Add Deployment Guide for Multiple Computers

**Objective:** Make it easy to add a new computer to the swarm.

**Files:**
- Create: `docs/multi_host_codex_swarm.md`
- Modify: `docs/multi_turn_codex.md`

**Guide should include:**

1. Clone repo on the new computer.
2. Install requirements and Codex.
3. Set env vars:
   - `LOCAL_RUNNER_API_TOKEN`
   - `LOCAL_RUNNER_WORKER_ID`
   - `LOCAL_RUNNER_CAPABILITIES`
4. Start local runner FastAPI.
5. Expose via Cloudflare Tunnel/Tailscale/ngrok.
6. Add endpoint to cloud worker registry.
7. Verify:
   - `GET /health`
   - protected `GET /status`
   - `POST /sessions`
   - two-turn round trip.

---

## Task 7: End-to-End Multi-Computer Smoke Test

**Objective:** Prove Hermes can coordinate at least two local Codex workers continuously.

**Prerequisite:** At least two registered worker endpoints.

**Test protocol:**

1. Create session `swarm-smoke-a` on worker A.
2. Create session `swarm-smoke-b` on worker B.
3. Send marker `A_MARKER_<timestamp>` to A.
4. Send marker `B_MARKER_<timestamp>` to B.
5. Ask A to summarize B's latest transcript after Hermes relays it.
6. Ask B to critique A's latest result after Hermes relays it.
7. Verify both transcripts show at least two turns and contain relayed context.

---

## Routing Policy

Default routing rules:

| Task type | Preferred capability |
|---|---|
| simulation / GPU experiment | `cuda` or `simulation` |
| paper / report writing | `paper` or `markdown` |
| ROS / hardware dry-run | `ros` plus `hardware-dry-run` |
| code refactor | `codex` |
| review | `review` or any idle `codex` worker |

If no capability match exists, Hermes should choose an active idle worker and state the assumption.

---

## Safety Model

- One bearer token per worker.
- Registry stores env var names, not token values.
- Local runners still reject missing/invalid bearer tokens.
- Local APIs do not accept arbitrary shell commands.
- Hardware-capable workers must advertise `hardware-dry-run` unless the user explicitly approves real hardware operation.
- Cloud Hermes must not broadcast secrets from one worker transcript to another.

---

## Acceptance Criteria

- Cloud Hermes can list registered workers and their capabilities.
- Cloud Hermes can create/read sessions on a selected worker.
- Cloud Hermes can append multiple turns to the same worker session.
- Cloud Hermes can maintain two active sessions on two different worker endpoints.
- Cloud Hermes can gather transcript from worker A and relay a sanitized summary to worker B.
- The old single-runner `auto-runner.qiaoing.work` flow still works.

---

## Recommended Implementation Order

1. Local runner capability metadata in `/status`.
2. Worker registry.
3. Session router.
4. Session index.
5. Fan-out/gather helpers.
6. Multi-host deployment guide.
7. Two-worker smoke test.

