# Research Autopilot Repository Initialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize a local multi-agent research repository for learning-based MPC studies on multimodal underwater robots.

**Architecture:** The repository is split into documentation/task orchestration, Python simulation code, experiment and paper assets, and local execution scripts. Initialization should create a reproducible skeleton with passing placeholder tests, queue-based task dispatch, and Git tracking without triggering any real hardware execution.

**Tech Stack:** Python, pytest, NumPy, matplotlib, YAML, Git, Bash wrappers, Markdown, LaTeX.

---

### Task 1: Documentation and Task Scaffolding

**Files:**
- Create: `README.md`
- Create: `AGENTS.md`
- Create: `project_state.json`
- Create: `progress.md`
- Create: `tasks/task_queue.json`
- Create: `tasks/research_prd.json`
- Create: `tasks/completed_tasks.json`
- Create: `prompts/codex/SIM-001.md`
- Create: `prompts/codex/SIM-002.md`
- Create: `prompts/codex/TEMPLATE.md`
- Create: `prompts/opencode/FIG-001.md`
- Create: `prompts/opencode/TEMPLATE.md`
- Create: `prompts/hermes/orchestrator_review.md`
- Create: `prompts/hermes/next_task_generation.md`
- Create: `research/literature/screened_papers.csv`
- Create: `research/literature/literature_summary.md`
- Create: `research/novelty/candidate_ideas.md`
- Create: `research/novelty/idea_score_matrix.csv`
- Create: `research/theory/problem_formulation.md`
- Create: `research/theory/method_derivation.md`
- Create: `figures/README.md`
- Create: `paper/main.tex`
- Create: `paper/references.bib`
- Create: `paper/sections/intro.tex`
- Create: `paper/sections/related_work.tex`
- Create: `paper/sections/method.tex`
- Create: `paper/sections/experiments.tex`
- Create: `paper/sections/results.tex`
- Create: `paper/sections/conclusion.tex`
- Create: `experiments/simulation/sim_protocol.md`
- Create: `experiments/simulation/baseline_methods.md`
- Create: `experiments/simulation/metrics.md`
- Create: `experiments/simulation/ablation_plan.md`
- Create: `experiments/hardware/hardware_protocol.md`
- Create: `experiments/hardware/safety_checklist.md`
- Create: `experiments/hardware/data_logging_format.md`
- Create: `experiments/hardware/sim2real_gap_analysis.md`

- [ ] **Step 1: Create the repository directories and markdown/json/csv scaffolding**
- [ ] **Step 2: Fill each file with the requested repository-specific content**
- [ ] **Step 3: Cross-check prompt paths and task queue references for consistency**

### Task 2: Python Package Skeleton and Tests

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/dynamics/__init__.py`
- Create: `src/dynamics/underwater_vehicle.py`
- Create: `src/controllers/__init__.py`
- Create: `src/controllers/pid.py`
- Create: `src/controllers/mpc.py`
- Create: `src/learning/__init__.py`
- Create: `src/learning/residual_model.py`
- Create: `src/experiments/__init__.py`
- Create: `src/experiments/run_tracking.py`
- Create: `src/visualization/__init__.py`
- Create: `src/visualization/plot_trajectory.py`
- Create: `src/utils/__init__.py`
- Create: `src/utils/config.py`
- Create: `src/utils/logger.py`
- Create: `configs/default.yaml`
- Create: `configs/sim_tracking.yaml`
- Create: `configs/controllers.yaml`
- Create: `tests/test_project_structure.py`
- Create: `tests/test_underwater_vehicle.py`

- [ ] **Step 1: Write placeholder tests that define the minimum expected structure and dynamics API**
- [ ] **Step 2: Implement the minimal placeholder modules needed to satisfy those tests**
- [ ] **Step 3: Keep the code lightweight and dependency-free beyond the requested stack**

### Task 3: Local Execution Scripts and Repository Hygiene

**Files:**
- Create: `.gitignore`
- Create: `scripts/local_orchestrator.py`
- Create: `scripts/run_local_loop.sh`
- Create: `scripts/run_codex_task.sh`
- Create: `scripts/run_opencode_task.sh`
- Create: `scripts/run_simulation.py`
- Create: `scripts/make_figures.py`
- Create: `scripts/compile_paper.sh`
- Create: `data/raw/.gitkeep`
- Create: `data/processed/.gitkeep`
- Create: `results/raw/.gitkeep`
- Create: `results/processed/.gitkeep`
- Create: `results/metrics_summary.csv`
- Create: `logs/.gitkeep`

- [ ] **Step 1: Implement a readable queue-driven orchestrator that logs output and updates task state**
- [ ] **Step 2: Add wrapper scripts and placeholder helpers without hard-coded credentials**
- [ ] **Step 3: Add repository ignore rules that preserve tracked artifact placeholders**

### Task 4: Verification and Git Initialization

**Files:**
- Verify: `tests/test_project_structure.py`
- Verify: `tests/test_underwater_vehicle.py`

- [ ] **Step 1: Run `python -m pytest -q` and fix any failures**
- [ ] **Step 2: Initialize Git if `.git` is absent**
- [ ] **Step 3: Run `git status`**
- [ ] **Step 4: Commit with `chore: initialize research autopilot repository`, unless Git identity is missing**
