# OpenCode Repository Review

## Executive Summary

The repository structure is broadly aligned with the intended multi-agent research workflow. Core top-level areas for prompts, tasks, research, experiments, paper assets, results, scripts, source code, and tests are present. Safety intent is documented in `AGENTS.md`, `README.md`, and `experiments/hardware/safety_checklist.md`, and the local orchestrator includes a basic guard for `requires_human_approval` tasks.

The main concerns are operational readiness and automation safety rather than missing structure. The repository is not fully ready to run `python scripts/local_orchestrator.py` unattended because the active Python environment cannot run `pytest`, the shell loop script performs automatic `git pull`, `git commit`, and `git push`, and task status handling in the orchestrator is inconsistent with the queue schema. There are also a few workflow/documentation mismatches that should be cleaned up before autonomous execution begins.

## Issues Found

1. `python -m pytest -q` currently fails in the active environment.

   - Result:

     ```text
     C:\Users\26938\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\python.exe: No module named pytest
     ```

   - Impact: the repository does not currently satisfy its own documented quality gate from `AGENTS.md` and `README.md` when run with the active interpreter.
   - Relevant files: `requirements.txt`, `pyproject.toml`, `AGENTS.md`, `README.md`

2. `scripts/run_local_loop.sh` is unsafe for autonomous use in its current form.

   - It always attempts `git pull --rebase`, `git add -A`, `git commit`, and `git push`.
   - It commits all changes in the repo, not only task-related changes.
   - It suppresses failures with `|| true`, which can mask real problems.
   - It can publish partially reviewed or unintended changes.
   - Relevant file: `scripts/run_local_loop.sh`

3. The orchestrator writes task statuses that are not present in the current queue schema.

   - Queue tasks currently use `status: "pending"`.
   - The orchestrator writes `blocked`, `failed`, and `done`.
   - This is workable technically, but the schema is undocumented and inconsistent with the initialization examples.
   - Impact: downstream tooling or humans may not know the allowed state machine.
   - Relevant files: `scripts/local_orchestrator.py`, `tasks/task_queue.json`

4. `README.md` under-describes the actual initialized source tree.

   - The README tree omits `src/`, `tests/`, `configs/`, `logs/`, and `data/` even though they exist and are already part of the workflow.
   - Impact: a new agent or collaborator gets an incomplete picture of the real structure.
   - Relevant file: `README.md`

5. The repository already contains implementation artifacts, but `project_state.json` still reports only `initialization`.

   - `src/dynamics/underwater_vehicle.py` and related tests already exist.
   - `progress.md` records `SIM-001` as completed.
   - `tasks/task_queue.json` still shows `SIM-001` as `pending`.
   - Impact: repository state, queue state, and progress log are not synchronized.
   - Relevant files: `project_state.json`, `tasks/task_queue.json`, `progress.md`, `src/dynamics/underwater_vehicle.py`

6. The queue is clear for a first pass but not yet very extensible.

   - Good: each task has `id`, `assigned_to`, `expected_outputs`, and `quality_checks`.
   - Missing for long-running research workflows: dependency fields, retry policy, blocking reason, artifact locations, and explicit allowed status values.
   - Relevant file: `tasks/task_queue.json`

7. `scripts/local_orchestrator.py` assumes agent CLIs are available but does not preflight them.

   - `resolve_cli_command()` falls back to unresolved command names if not found.
   - Failure is deferred until execution time rather than producing a clearer setup error.
   - Relevant file: `scripts/local_orchestrator.py`

8. The repository mixes documented shell examples with a Unix shell script in a Windows environment.

   - `run_local_loop.sh` is a Bash script while this machine is Windows-first.
   - That may be acceptable if Git Bash or WSL is assumed, but that assumption is not documented.
   - Relevant files: `scripts/run_local_loop.sh`, `README.md`

## Safety Concerns

1. Hardware execution is documented as disallowed without human approval, and the orchestrator does check `requires_human_approval`.

   - This is good.
   - However, the protection is only as strong as task metadata. If a hardware-related task is misclassified as ordinary `coding`, the orchestrator will run it.

2. There is no dedicated guard on task `type` despite `AGENTS.md` explicitly referencing `type=hardware_execution`.

   - `local_orchestrator.py` blocks only on `requires_human_approval`.
   - It does not also block on `type == "hardware_execution"`.
   - This is a small but real policy mismatch.

3. `run_local_loop.sh` is the biggest practical automation risk.

   - Automatic pull/commit/push behavior is riskier than the orchestrator itself.
   - If used casually, it can create noisy history, commit unrelated work, and obscure failures.

4. The hardware safety checklist is directionally correct but minimal.

   - It states the right constraints.
   - It does not yet define a concrete approval record, sign-off template, or stop conditions for any future dry-run to real-run transition.

## Suggested Improvements

1. Make the project executable in one documented environment before starting autonomous work.

   - Install dependencies into the intended interpreter or document the required environment explicitly.
   - Confirm `python -m pytest -q` works from the repo root.

2. Tighten automation safety before using the local loop.

   - Remove or disable automatic `git pull`, `git add -A`, `git commit`, and `git push` from unattended execution.
   - If a loop script is kept, make it orchestration-only and leave Git actions manual.

3. Align task state management.

   - Document allowed statuses such as `pending`, `in_progress`, `done`, `failed`, and `blocked`.
   - Keep `progress.md`, `task_queue.json`, and `project_state.json` consistent after task completion.

4. Add a second safety gate in the orchestrator.

   - Block execution when `type == "hardware_execution"` in addition to `requires_human_approval == true`.

5. Improve queue extensibility now, before task volume grows.

   - Add optional fields such as `depends_on`, `artifacts`, `blocked_reason`, and `allowed_status_transitions`.
   - Consider a `stage` or `workstream` link back to `tasks/research_prd.json`.

6. Update README structure documentation.

   - Include `src/`, `tests/`, `configs/`, `data/`, and `logs/` in the documented tree.
   - Clarify whether Bash, WSL, or Git Bash is expected on Windows.

7. Add lightweight preflight checks to the orchestrator.

   - Verify queue file exists.
   - Verify prompt file exists.
   - Verify the assigned agent CLI exists.
   - Optionally verify Git availability before Git-dependent changed-file checks.

8. Clarify output storage conventions.

   - Current layout is reasonable: figures in `figures/`, results in `results/`, paper material in `paper/`.
   - Consider documenting whether summary CSVs like `results/metrics_summary.csv` belong at the top of `results/` or under `results/processed/`.

## Recommended Next Tasks

1. Make the Python environment reproducible and verify `pytest` works.

2. Update `scripts/run_local_loop.sh` to remove automatic Git side effects before any unattended use.

3. Synchronize current task state across `progress.md`, `task_queue.json`, and `project_state.json`.

4. Add one more orchestrator guard for `type == "hardware_execution"`.

5. Expand the queue schema slightly before more agents start writing to it.

6. Update `README.md` so the documented structure matches the actual repository.

## Readiness Assessment

### Does the repository structure support the intended workflow?

Yes, broadly. The main directories and placeholder assets are present and aligned with the multi-agent research workflow.

### Is the local task queue clear and extensible?

Clear for initial use, but only moderately extensible. It is good enough to start a few tasks, but it should gain a more explicit status model and dependency metadata soon.

### Does the local orchestrator avoid obvious unsafe behavior?

Partially. The orchestrator itself has a basic human-approval guard, but the surrounding loop script introduces obvious unsafe automation behavior.

### Do hardware experiment tasks require human approval and avoid automatic execution?

At the policy level, yes. At the enforcement level, mostly yes, but only if task metadata is correct.

### Are generated outputs stored in reasonable locations?

Yes. `results/`, `figures/`, and `paper/` are appropriate. Placeholder `.gitkeep` files are present in `data/raw`, `data/processed`, `results/raw`, and `results/processed`.

### Is the project ready for Codex/OpenCode task execution?

Mostly for manual, supervised task execution. Not fully for unattended autopilot execution.

### Are there missing directories, missing `.gitkeep` files, or broken paths?

No critical missing directories were found in the reviewed areas. Referenced core directories exist. The main mismatch is state/documentation consistency rather than broken paths.

### Are there shell quoting or subprocess safety issues?

No major shell quoting bug stands out in the reviewed Python subprocess code. The bigger issue is unsafe automation behavior in `run_local_loop.sh`, not quoting.

## Ready To Run `python scripts/local_orchestrator.py`?

Not yet as a reliable autonomous workflow entrypoint.

Reasons:

- `python -m pytest -q` does not run in the active environment because `pytest` is missing.
- The repository state is inconsistent across queue, progress log, and project state.
- The surrounding loop script is too aggressive for safe unattended use.
- Hardware blocking logic should be strengthened slightly to match documented policy.

For supervised/manual development, the repository is close. For autonomous local execution, fix the environment and loop-safety issues first.

## Small Fixes Made

No code or configuration changes were made during this review. Only this review document was added.
