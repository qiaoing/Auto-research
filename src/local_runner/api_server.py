"""FastAPI server for local runner status, trigger, logs, and GitHub webhooks."""

from __future__ import annotations

import hmac
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from . import git_ops
from .config import RunnerConfig, load_config
from .locks import is_runner_busy
from .logging_utils import ensure_logs_dir, log_summary
from .runner_status import read_runner_status
from .session_worker import append_session_turn, ensure_session, read_session_transcript, session_summary
from .state_machine import count_by_status
from .task_store import get_tasks, summarize_tasks
from .time_utils import utc_now_iso
from .webhook import changed_paths, has_relevant_path, verify_github_signature

SERVICE_NAME = "auto-research-local-runner"
SAFE_TASK_ID = re.compile(r"^[A-Za-z0-9_.-]+$")
_launch_lock = threading.Lock()
_active_process: subprocess.Popen[Any] | None = None


class CreateSessionRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=120)
    codex_instance: str = Field(default="default", min_length=1, max_length=80)


class AppendTurnRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    turn_id: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, max_length=240)
    codex_instance: str = Field(default="default", min_length=1, max_length=80)
    quality_checks: list[Any] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)


def create_app(config: RunnerConfig | None = None, warn_missing_secrets: bool = False) -> FastAPI:
    config = config or load_config()
    app = FastAPI(title=SERVICE_NAME)
    app.state.config = config

    if warn_missing_secrets and not config.api_token:
        print("WARNING: LOCAL_RUNNER_API_TOKEN is not configured; protected APIs will reject requests.", file=sys.stderr)
    if warn_missing_secrets and not config.webhook_secret:
        print("WARNING: GITHUB_WEBHOOK_SECRET is not configured; GitHub webhook will reject requests.", file=sys.stderr)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": SERVICE_NAME, "time": utc_now_iso()}

    def protected(authorization: str | None = Header(default=None)) -> None:
        require_bearer_token(app.state.config, authorization)

    @app.get("/status")
    def status_endpoint(_: None = Depends(protected)) -> dict[str, Any]:
        repo_root = app.state.config.repo_root
        tasks = get_tasks(repo_root)
        runner = read_runner_status(repo_root)
        dirty = git_ops.is_dirty(repo_root) if git_ops.is_git_repo(repo_root) else False
        changed_files = git_ops.changed_files(repo_root)[:20] if dirty else []
        return {
            "runner": {
                "busy": is_runner_busy(repo_root),
                "current_task": runner.get("current_task"),
                "last_run_at": runner.get("last_run_at"),
                "last_run_status": runner.get("last_run_status"),
                "last_run_id": runner.get("last_run_id"),
            },
            "git": {
                "branch": git_ops.current_branch(repo_root),
                "head": git_ops.current_head(repo_root),
                "dirty": dirty,
                "changed_files": changed_files,
            },
            "tasks": count_by_status(tasks),
        }

    @app.get("/tasks")
    def tasks_endpoint(_: None = Depends(protected)) -> dict[str, Any]:
        return {"tasks": summarize_tasks(app.state.config.repo_root)}

    @app.post("/run-once")
    def run_once_endpoint(_: None = Depends(protected)) -> dict[str, Any]:
        return launch_run_once(app.state.config.repo_root)

    @app.post("/sessions")
    def create_session_endpoint(payload: CreateSessionRequest, _: None = Depends(protected)) -> dict[str, Any]:
        return {"session": ensure_session(app.state.config.repo_root, payload.conversation_id, payload.codex_instance)}

    @app.get("/sessions/{conversation_id}")
    def session_endpoint(
        conversation_id: str,
        codex_instance: str = "default",
        _: None = Depends(protected),
    ) -> dict[str, Any]:
        return {"session": session_summary(app.state.config.repo_root, conversation_id, codex_instance)}

    @app.get("/sessions/{conversation_id}/transcript")
    def session_transcript_endpoint(
        conversation_id: str,
        codex_instance: str = "default",
        _: None = Depends(protected),
    ) -> dict[str, Any]:
        return read_session_transcript(app.state.config.repo_root, conversation_id, codex_instance)

    @app.post("/sessions/{conversation_id}/turns")
    def append_session_turn_endpoint(
        conversation_id: str,
        payload: AppendTurnRequest,
        _: None = Depends(protected),
    ) -> dict[str, Any]:
        result = append_session_turn(
            app.state.config.repo_root,
            conversation_id=conversation_id,
            prompt=payload.prompt,
            codex_instance=payload.codex_instance,
            turn_id=payload.turn_id,
            title=payload.title,
            quality_checks=payload.quality_checks,
            expected_outputs=payload.expected_outputs,
        )
        return {"turn": result.__dict__}

    @app.get("/logs/{task_id:path}")
    def logs_endpoint(task_id: str, _: None = Depends(protected)) -> dict[str, Any]:
        if not SAFE_TASK_ID.fullmatch(task_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid task_id")

        repo_root = app.state.config.repo_root
        logs_dir = ensure_logs_dir(repo_root).resolve()
        matches = sorted(
            [
                *(logs_dir.glob(f"{task_id}_agent.log")),
                *(logs_dir.glob(f"{task_id}_check_*.log")),
                *(logs_dir.glob(f"{task_id}_orchestrator.log")),
            ]
        )
        safe_logs = []
        for path in matches:
            resolved = path.resolve()
            if logs_dir not in (resolved, *resolved.parents):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid log path")
            safe_logs.append(log_summary(resolved))
        return {"task_id": task_id, "logs": safe_logs}

    @app.post("/webhook/github")
    async def github_webhook(
        request: Request,
        x_hub_signature_256: str | None = Header(default=None),
        x_github_event: str | None = Header(default=None),
    ) -> dict[str, Any]:
        body = await request.body()
        verify_webhook_signature(body, x_hub_signature_256, app.state.config.webhook_secret)

        if x_github_event != "push":
            return {"accepted": False, "ignored": True, "reason": "unsupported event"}

        payload = await request.json()
        changed_paths = webhook_changed_paths(payload)
        if not has_relevant_webhook_path(changed_paths):
            return {"accepted": False, "ignored": True, "reason": "no relevant path changes"}
        return launch_run_once(app.state.config.repo_root)

    return app


def require_bearer_token(config: RunnerConfig, authorization: str | None) -> None:
    token = config.api_token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="LOCAL_RUNNER_API_TOKEN is not configured")
    expected = f"Bearer {token}"
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid authorization token")


def verify_webhook_signature(body: bytes, signature_header: str | None, secret: str | None) -> None:
    if not secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="GITHUB_WEBHOOK_SECRET is not configured")
    if not verify_github_signature(body, signature_header, secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid GitHub signature")


def webhook_changed_paths(payload: dict[str, Any]) -> set[str]:
    return changed_paths(payload)


def has_relevant_webhook_path(paths: set[str]) -> bool:
    return has_relevant_path(paths)


def launch_run_once(repo_root: Path) -> dict[str, Any]:
    global _active_process

    run_id = time.strftime("%Y%m%d-%H%M%S")
    active_process_running = _active_process is not None and _active_process.poll() is None
    if active_process_running or is_runner_busy(repo_root) or not _launch_lock.acquire(blocking=False):
        return {"accepted": False, "busy": True, "message": "runner is already running"}

    try:
        script = repo_root / "scripts" / "local_runner_service.py"
        _active_process = subprocess.Popen(
            [sys.executable, str(script), "--once", "--repo-root", str(repo_root), "--run-id", run_id],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=os.name != "nt",
        )
    finally:
        _launch_lock.release()

    return {"accepted": True, "busy": False, "message": "runner started", "run_id": run_id}


app = create_app()


def main(argv: list[str] | None = None) -> int:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Start local runner API server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args(argv)

    global app
    app = create_app(load_config(repo_root=args.repo_root, host=args.host, port=args.port), warn_missing_secrets=True)
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
