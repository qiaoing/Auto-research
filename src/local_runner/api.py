"""Compatibility module for `python -m local_runner.api`."""

from __future__ import annotations

from .api_server import app, main

__all__ = ["app", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
