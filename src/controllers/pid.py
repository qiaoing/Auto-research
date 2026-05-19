"""PID controller placeholder."""

from __future__ import annotations

import numpy as np


class PlaceholderPIDController:
    """Minimal placeholder PID-like interface for future tracking work."""

    def __init__(self, gains: dict | None = None) -> None:
        self.gains = gains or {"kp": 0.0, "ki": 0.0, "kd": 0.0}

    def compute(self, error: np.ndarray) -> np.ndarray:
        error_vector = np.asarray(error, dtype=float)
        return self.gains["kp"] * error_vector
