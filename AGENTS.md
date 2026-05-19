# AGENTS.md

## Project Role

This repository is a local execution workspace for a multi-agent research autopilot system.

Cloud Hermes acts as the research orchestrator.
Local Codex/OpenCode agents implement code, simulations, plotting scripts, and paper infrastructure.

## Research Domain

- Multimodal underwater robots / HAUV
- Learning-based MPC
- RL-MPC
- Nonlinear underwater dynamics
- Disturbance rejection
- Simulation and hardware experiment design

## Rules for Local Agents

1. Do not execute real hardware experiments automatically.
2. Hardware-related tasks must stop at design, scripts, checks, or dry-run unless human approval is explicitly given.
3. Keep code modular and testable.
4. Prefer simple, reproducible Python simulation code.
5. Every coding task should include tests when practical.
6. Do not hard-code API keys, tokens, or credentials.
7. Store generated results in `results/`.
8. Store figures in `figures/`.
9. Store paper materials in `paper/`.
10. Update `progress.md` after completing or failing a task.
11. Use Git commits frequently.
12. Do not modify unrelated files for a task.

## Quality Checks

Before marking a coding task done, run relevant tests, for example:

```bash
pytest -q
```

For plotting tasks, verify expected output files exist.
For paper tasks, compile or at least validate file references when possible.

## Safety

Any task with `type=hardware_execution` or `requires_human_approval=true` must not be executed automatically.
Instead, mark it as blocked and write required human approval steps.
