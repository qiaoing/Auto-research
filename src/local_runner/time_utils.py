"""Time helpers used across runner modules."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return a timezone-aware ISO timestamp with second precision."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
