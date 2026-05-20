"""Local runner loop that synchronizes git and runs one orchestrator pass."""

from __future__ import annotations

import argparse
import signal
import time
from pathlib import Path
from typing import Any

from . import git_ops
from .config import resolve_repo_root
from .locks import RunnerLock, runner_lock_path
from .logging_utils import configure_service_logger
from .orchestrator import run_one
from .runner_status import write_runner_status
from .time_utils import utc_now_iso

_STOP_REQUESTED = False


def _handle_stop(signum: int, frame: object) -> None:
    global _STOP_REQUESTED
    _STOP_REQUESTED = True


def install_signal_handlers() -> None:
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)


def _log_git_result(logger: Any, label: str, result: Any) -> None:
    if result is None:
        logger.info("%s skipped", label)
        return
    output = (result.stdout or "").strip()
    logger.info("%s exited with %s", label, result.returncode)
    if output:
        logger.info("%s output: %s", label, output)


def run_once(repo_root: Path, run_id: str | None = None) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    logger = configure_service_logger(repo_root)
    lock = RunnerLock(runner_lock_path(repo_root))
    run_id = run_id or time.strftime("%Y%m%d-%H%M%S")

    if not lock.acquire():
        logger.info("runner busy; run %s not started", run_id)
        return {"accepted": False, "busy": True, "run_id": run_id, "status": "busy"}

    write_runner_status(repo_root, current_task=None, last_run_id=run_id, last_run_at=utc_now_iso(), last_run_status="running")
    logger.info("runner run %s started", run_id)
    try:
        try:
            _log_git_result(logger, "git pull --rebase", git_ops.pull_rebase(repo_root))
        except Exception as exc:  # noqa: BLE001 - runner must preserve local task status even if git sync fails.
            logger.exception("git pull --rebase failed: %s", exc)

        result = run_one(repo_root, runner_id="local-runner")
        write_runner_status(
            repo_root,
            current_task=None,
            last_task_id=result.get("task_id"),
            last_run_id=run_id,
            last_run_at=utc_now_iso(),
            last_run_status=str(result.get("status")),
        )

        try:
            _log_git_result(logger, "git add -A", git_ops.add_all(repo_root))
            _log_git_result(logger, "git commit", git_ops.commit(repo_root, "agent: local runner update"))
            _log_git_result(logger, "git push", git_ops.push(repo_root))
        except Exception as exc:  # noqa: BLE001
            logger.exception("git publish step failed: %s", exc)

        logger.info("runner run %s finished with %s", run_id, result.get("status"))
        return {"accepted": True, "busy": False, "run_id": run_id, "status": result.get("status"), "result": result}
    except Exception as exc:  # noqa: BLE001
        write_runner_status(
            repo_root,
            current_task=None,
            last_run_id=run_id,
            last_run_at=utc_now_iso(),
            last_run_status="error",
            last_error=str(exc),
        )
        logger.exception("runner run %s failed: %s", run_id, exc)
        return {"accepted": True, "busy": False, "run_id": run_id, "status": "error", "error": str(exc)}
    finally:
        lock.release()


def run_loop(repo_root: Path, interval: int) -> None:
    logger = configure_service_logger(repo_root)
    logger.info("runner loop started with interval=%s", interval)
    while not _STOP_REQUESTED:
        run_once(repo_root)
        for _ in range(max(interval, 1)):
            if _STOP_REQUESTED:
                break
            time.sleep(1)
    logger.info("runner loop stopped")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local research runner service.")
    parser.add_argument("--repo-root", default=None, help="Repository root. Defaults to current directory.")
    parser.add_argument("--once", action="store_true", help="Run one pass then exit.")
    parser.add_argument("--interval", type=int, default=30, help="Polling interval in seconds for loop mode.")
    parser.add_argument("--run-id", default=None, help="Optional run id supplied by the API server.")
    args = parser.parse_args(argv)

    repo_root = resolve_repo_root(args.repo_root)
    install_signal_handlers()
    if args.once:
        result = run_once(repo_root, run_id=args.run_id)
        print(result)
        return 0 if result.get("status") != "error" else 1
    run_loop(repo_root, args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
