"""Tracking experiment placeholder entry point."""

from __future__ import annotations

from pathlib import Path


def main(config_path: str = "configs/sim_tracking.yaml") -> str:
    return f"Tracking experiment placeholder. Config: {Path(config_path)}"


if __name__ == "__main__":
    print(main())
