"""MPC controller placeholder."""

from __future__ import annotations

import numpy as np


class PlaceholderMPCController:
    """Minimal placeholder MPC-style controller interface."""

    def __init__(self, horizon: int = 10) -> None:
        self.horizon = int(horizon)

    def plan(self, state: np.ndarray, reference: np.ndarray) -> np.ndarray:
        _ = np.asarray(state, dtype=float)
        reference_vector = np.asarray(reference, dtype=float)
        return np.zeros_like(reference_vector)
