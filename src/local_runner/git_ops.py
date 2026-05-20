"""Constrained git operations used by the runner service."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(repo_root: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def is_git_repo(repo_root: Path) -> bool:
    return _run_git(repo_root, ["rev-parse", "--is-inside-work-tree"]).returncode == 0


def current_branch(repo_root: Path) -> str | None:
    result = _run_git(repo_root, ["branch", "--show-current"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def current_head(repo_root: Path) -> str | None:
    result = _run_git(repo_root, ["rev-parse", "--short", "HEAD"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def is_dirty(repo_root: Path) -> bool:
    result = _run_git(repo_root, ["status", "--porcelain"])
    return bool(result.stdout.strip())


def changed_files(repo_root: Path) -> list[str]:
    result = _run_git(repo_root, ["status", "--porcelain"])
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        files.append(line[3:].strip())
    return files


def has_remote(repo_root: Path) -> bool:
    result = _run_git(repo_root, ["remote"])
    return bool(result.stdout.strip())


def pull_rebase(repo_root: Path) -> subprocess.CompletedProcess[str] | None:
    if not has_remote(repo_root):
        return None
    return _run_git(repo_root, ["pull", "--rebase"])


def add_all(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return _run_git(repo_root, ["add", "-A"])


def commit(repo_root: Path, message: str) -> subprocess.CompletedProcess[str] | None:
    if not is_dirty(repo_root):
        return None
    return _run_git(repo_root, ["commit", "-m", message])


def push(repo_root: Path) -> subprocess.CompletedProcess[str] | None:
    if not has_remote(repo_root):
        return None
    return _run_git(repo_root, ["push"])
