"""Residual model placeholder."""

from __future__ import annotations

import numpy as np


class PlaceholderResidualModel:
    """Stub residual model that currently predicts zero correction."""

    def predict(self, features: np.ndarray) -> np.ndarray:
        feature_array = np.asarray(features, dtype=float)
        return np.zeros_like(feature_array)
