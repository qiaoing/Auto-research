"""Reusable trajectory plotting scaffold."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np


def build_trajectory_figure(points: Iterable[Iterable[float]]):
    trajectory = np.asarray(list(points), dtype=float)
    fig, ax = plt.subplots()
    if trajectory.size:
        ax.plot(trajectory[:, 0], trajectory[:, 1], label="trajectory")
        ax.legend()
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Trajectory Placeholder")
    return fig, ax
