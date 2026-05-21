# Multi-Host Codex Swarm

This document describes the target architecture for one cloud Hermes instance coordinating continuous multi-turn Codex sessions across multiple local computers.

## Why this is needed

The direct session API lets Hermes talk repeatedly to one local runner:

```text
POST /sessions/{conversation_id}/turns
```

For complex work, we need one cloud Hermes to coordinate several independent local Codex workers, for example:

- desktop GPU workstation for simulation;
- laptop for writing/refactoring;
- lab machine for ROS/hardware dry-run;
- another server for review or long-running tests.

## Target shape

```text
Cloud Hermes
  ├── worker registry
  ├── session router
  ├── project/session index
  └── fan-out/gather coordinator
        ├── worker: desktop-gpu → local Codex sessions
        ├── worker: laptop-win  → local Codex sessions
        └── worker: lab-ros     → local Codex sessions
```

## Addressing model

A conversation is no longer globally identified by `conversation_id` alone. The full routing key is:

```text
worker_id + conversation_id + codex_instance
```

Example:

```json
{
  "worker_id": "desktop-gpu",
  "conversation_id": "leaf-mpc-sim",
  "codex_instance": "sim"
}
```

## Worker registry

Cloud Hermes should keep a registry like:

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

The registry must store `token_env`, not raw token values.

## Local runner requirements

Each computer should expose the same local-runner API:

- `GET /health`
- protected `GET /status`
- protected `POST /sessions`
- protected `POST /sessions/{conversation_id}/turns`
- protected `GET /sessions/{conversation_id}/transcript`

Recommended local environment variables:

```bash
LOCAL_RUNNER_API_TOKEN=...
LOCAL_RUNNER_WORKER_ID=desktop-gpu
LOCAL_RUNNER_LABEL="Desktop GPU workstation"
LOCAL_RUNNER_CAPABILITIES=codex,python,cuda,simulation
LOCAL_RUNNER_MAX_CONCURRENT_SESSIONS=1
```

## Cloud-side workflow example

1. Hermes receives a complex request: "推进 LEAF-MPC 仿真、论文和评审".
2. Hermes picks workers:
   - `desktop-gpu` for simulation;
   - `laptop-win` for manuscript editing;
   - `reviewer-node` for review.
3. Hermes creates one session per role.
4. Hermes sends turn 1 to each worker.
5. Hermes gathers transcripts and artifact summaries.
6. Hermes sends cross-context turns:
   - simulation output → manuscript worker;
   - manuscript draft → reviewer worker;
   - reviewer critique → simulation/manuscript workers.
7. Hermes reports progress to the user.

## Two-worker smoke test

For every new deployment, run:

1. Create session `swarm-smoke-a` on worker A.
2. Create session `swarm-smoke-b` on worker B.
3. Send unique marker A to worker A.
4. Send unique marker B to worker B.
5. Read transcripts from both.
6. Relay A's summary to B and B's summary to A.
7. Confirm both transcripts contain at least two turns and the relayed context.

## Safety rules

- Use one bearer token per worker.
- Do not place raw tokens in Git or persistent memory.
- Do not expose arbitrary shell execution over HTTP.
- Use capability tags for routing; do not send hardware work to a machine unless it advertises safe dry-run capability.
- Cross-feed summaries, not full raw transcripts, when transcripts may contain credentials or local paths.

See implementation plan: `docs/plans/2026-05-22-multi-host-codex-swarm.md`.
