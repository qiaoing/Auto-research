# Research Autopilot Progress Log

## Codebase Patterns

- This repository uses `tasks/task_queue.json` as the local task queue.
- Codex should be used for simulation code and complex implementation tasks.
- OpenCode should be used for plotting, refactoring, and paper infrastructure tasks.
- Hardware experiment execution requires human approval.

---

## Initialization

- Repository initialized.
- Project structure created.
- Waiting for Hermes to generate or update research tasks.

## Initialization Status

- Worker 1 documentation scaffold: completed.
- Task queue and prompt templates: created.
- Research, experiments, figures, and paper placeholders: created.

## 2026-05-19

- SIM-001 completed: implemented a coupled 3-DOF planar underwater vehicle model in `src/dynamics/underwater_vehicle.py`.
- Added SIM-001 tests for shape, zero-velocity equilibrium, coupled deterministic dynamics, and yaw-angle integration in `tests/test_underwater_vehicle.py`.
- Verified all SIM-001 test functions by direct execution with `conda run -n MPC python -c ...`; `pytest` is currently unavailable in accessible environments.
- [2026-05-19 23:01:22] Task SIM-001 completed successfully.
