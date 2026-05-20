"""Cross-platform file lock for runner concurrency protection."""

from __future__ import annotations

import os
import time
from pathlib import Path

from .time_utils import utc_now_iso


class RunnerLock:
    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self.acquired = False

    def acquire(self) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        remove_stale_lock(self.lock_path)
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(str(self.lock_path), flags)
        except FileExistsError:
            return False

        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\n")
            handle.write(f"created_at={utc_now_iso()}\n")
        self.acquired = True
        return True

    def release(self) -> None:
        if self.acquired and self.lock_path.exists():
            self.lock_path.unlink()
        self.acquired = False

    def __enter__(self) -> "RunnerLock":
        self.acquire()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.release()


def runner_lock_path(repo_root: Path) -> Path:
    return repo_root / "logs" / "runner.lock"


def lock_stale_seconds() -> int:
    raw_value = os.environ.get("LOCAL_RUNNER_LOCK_STALE_SECONDS", "86400")
    try:
        return max(int(raw_value), 1)
    except ValueError:
        return 86400


def is_lock_stale(lock_path: Path) -> bool:
    if not lock_path.exists():
        return False
    age_seconds = time.time() - lock_path.stat().st_mtime
    return age_seconds > lock_stale_seconds()


def remove_stale_lock(lock_path: Path) -> bool:
    if is_lock_stale(lock_path):
        lock_path.unlink(missing_ok=True)
        return True
    return False


def is_runner_busy(repo_root: Path) -> bool:
    lock_path = runner_lock_path(repo_root)
    if remove_stale_lock(lock_path):
        return False
    return lock_path.exists()
