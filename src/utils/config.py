"""Configuration loading helpers."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_yaml_config(path: str | Path) -> dict:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("YAML config must decode to a mapping")
    return data
