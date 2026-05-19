from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_directories_exist():
    required_dirs = [
        ROOT / "tasks",
        ROOT / "prompts",
        ROOT / "prompts" / "codex",
        ROOT / "prompts" / "opencode",
        ROOT / "prompts" / "hermes",
        ROOT / "research",
        ROOT / "research" / "literature",
        ROOT / "research" / "novelty",
        ROOT / "research" / "theory",
        ROOT / "experiments",
        ROOT / "experiments" / "simulation",
        ROOT / "experiments" / "hardware",
        ROOT / "scripts",
        ROOT / "src",
        ROOT / "src" / "dynamics",
        ROOT / "src" / "controllers",
        ROOT / "src" / "learning",
        ROOT / "src" / "experiments",
        ROOT / "src" / "visualization",
        ROOT / "src" / "utils",
        ROOT / "configs",
        ROOT / "data",
        ROOT / "results",
        ROOT / "figures",
        ROOT / "paper",
        ROOT / "logs",
        ROOT / "tests",
    ]

    for directory in required_dirs:
        assert directory.is_dir(), f"Missing directory: {directory}"


def test_required_files_exist():
    required_files = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "project_state.json",
        ROOT / "progress.md",
        ROOT / "pyproject.toml",
        ROOT / "requirements.txt",
        ROOT / ".gitignore",
        ROOT / "tasks" / "task_queue.json",
        ROOT / "tasks" / "research_prd.json",
        ROOT / "tasks" / "completed_tasks.json",
        ROOT / "src" / "__init__.py",
        ROOT / "src" / "dynamics" / "__init__.py",
        ROOT / "src" / "dynamics" / "underwater_vehicle.py",
        ROOT / "src" / "controllers" / "__init__.py",
        ROOT / "src" / "controllers" / "pid.py",
        ROOT / "src" / "controllers" / "mpc.py",
        ROOT / "src" / "learning" / "__init__.py",
        ROOT / "src" / "learning" / "residual_model.py",
        ROOT / "src" / "experiments" / "__init__.py",
        ROOT / "src" / "experiments" / "run_tracking.py",
        ROOT / "src" / "visualization" / "__init__.py",
        ROOT / "src" / "visualization" / "plot_trajectory.py",
        ROOT / "src" / "utils" / "__init__.py",
        ROOT / "src" / "utils" / "config.py",
        ROOT / "src" / "utils" / "logger.py",
        ROOT / "configs" / "default.yaml",
        ROOT / "configs" / "sim_tracking.yaml",
        ROOT / "configs" / "controllers.yaml",
        ROOT / "scripts" / "local_orchestrator.py",
        ROOT / "scripts" / "run_local_loop.sh",
        ROOT / "paper" / "main.tex",
        ROOT / "figures" / "README.md",
        ROOT / "tests" / "test_project_structure.py",
        ROOT / "tests" / "test_underwater_vehicle.py",
    ]

    for file_path in required_files:
        assert file_path.is_file(), f"Missing file: {file_path}"
