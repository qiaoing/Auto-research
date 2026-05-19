"""Underwater vehicle dynamics models."""

from __future__ import annotations

import numpy as np


class PlanarUnderwaterVehicle3DOF:
    """Simple placeholder for a 3-DOF planar underwater vehicle model."""

    def __init__(
        self,
        mass_u: float = 20.0,
        mass_v: float = 25.0,
        inertia_r: float = 8.0,
        linear_damping: tuple[float, float, float] = (6.0, 8.0, 3.0),
        quadratic_damping: tuple[float, float, float] = (2.5, 3.0, 1.0),
    ) -> None:
        self.mass_u = float(mass_u)
        self.mass_v = float(mass_v)
        self.inertia_r = float(inertia_r)
        self.linear_damping = np.asarray(linear_damping, dtype=float)
        self.quadratic_damping = np.asarray(quadratic_damping, dtype=float)

    def dynamics(
        self,
        state: np.ndarray,
        control: np.ndarray,
        disturbance: np.ndarray | None = None,
    ) -> np.ndarray:
        state = np.asarray(state, dtype=float)
        control = np.asarray(control, dtype=float)

        if state.shape != (6,):
            raise ValueError("state must have shape (6,)")
        if control.shape != (2,):
            raise ValueError("control must have shape (2,)")

        disturbance_vector = np.zeros(3, dtype=float)
        if disturbance is not None:
            disturbance_vector = np.asarray(disturbance, dtype=float)
            if disturbance_vector.shape != (3,):
                raise ValueError("disturbance must have shape (3,)")

        x, y, psi, u, v, r = state
        tau_u, tau_r = control
        d_u, d_v, d_r = self.linear_damping
        q_u, q_v, q_r = self.quadratic_damping

        x_dot = np.cos(psi) * u - np.sin(psi) * v
        y_dot = np.sin(psi) * u + np.cos(psi) * v
        psi_dot = r

        surge_drag = d_u * u + q_u * abs(u) * u
        sway_drag = d_v * v + q_v * abs(v) * v
        yaw_drag = d_r * r + q_r * abs(r) * r

        u_dot = (tau_u - surge_drag + disturbance_vector[0]) / self.mass_u
        v_dot = (-sway_drag + disturbance_vector[1]) / self.mass_v
        r_dot = (tau_r - yaw_drag + disturbance_vector[2]) / self.inertia_r

        return np.array([x_dot, y_dot, psi_dot, u_dot, v_dot, r_dot], dtype=float)

    def step(
        self,
        state: np.ndarray,
        control: np.ndarray,
        dt: float,
        disturbance: np.ndarray | None = None,
    ) -> np.ndarray:
        state = np.asarray(state, dtype=float)
        if state.shape != (6,):
            raise ValueError("state must have shape (6,)")
        return state + float(dt) * self.dynamics(state, control, disturbance)
