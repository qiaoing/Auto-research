"""Underwater vehicle dynamics models."""

from __future__ import annotations

import numpy as np


class PlanarUnderwaterVehicle3DOF:
    """Coupled 3-DOF planar underwater vehicle model for simulation."""

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

        mass_terms = np.array([self.mass_u, self.mass_v, self.inertia_r], dtype=float)
        if np.any(mass_terms <= 0.0):
            raise ValueError("mass and inertia parameters must be positive")
        if self.linear_damping.shape != (3,):
            raise ValueError("linear_damping must have shape (3,)")
        if self.quadratic_damping.shape != (3,):
            raise ValueError("quadratic_damping must have shape (3,)")

        self.mass_matrix = np.diag(mass_terms)
        self.inverse_mass_matrix = np.diag(1.0 / mass_terms)

    @staticmethod
    def _validate_state(state: np.ndarray) -> np.ndarray:
        state = np.asarray(state, dtype=float)
        if state.shape != (6,):
            raise ValueError("state must have shape (6,)")
        return state

    @staticmethod
    def _validate_control(control: np.ndarray) -> np.ndarray:
        control = np.asarray(control, dtype=float)
        if control.shape != (2,):
            raise ValueError("control must have shape (2,)")
        return control

    @staticmethod
    def _validate_disturbance(disturbance: np.ndarray | None) -> np.ndarray:
        if disturbance is None:
            return np.zeros(3, dtype=float)

        disturbance_vector = np.asarray(disturbance, dtype=float)
        if disturbance_vector.shape != (3,):
            raise ValueError("disturbance must have shape (3,)")
        return disturbance_vector

    @staticmethod
    def _rotation_matrix(psi: float) -> np.ndarray:
        return np.array(
            [
                [np.cos(psi), -np.sin(psi), 0.0],
                [np.sin(psi), np.cos(psi), 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        )

    def _coriolis_vector(self, velocity: np.ndarray) -> np.ndarray:
        u, v, r = velocity
        return np.array(
            [
                -self.mass_v * v * r,
                self.mass_u * u * r,
                (self.mass_v - self.mass_u) * u * v,
            ],
            dtype=float,
        )

    def _damping_vector(self, velocity: np.ndarray) -> np.ndarray:
        return self.linear_damping * velocity + self.quadratic_damping * np.abs(
            velocity
        ) * velocity

    def dynamics(
        self,
        state: np.ndarray,
        control: np.ndarray,
        disturbance: np.ndarray | None = None,
    ) -> np.ndarray:
        state = self._validate_state(state)
        control = self._validate_control(control)
        disturbance_vector = self._validate_disturbance(disturbance)

        _, _, psi, u, v, r = state
        tau_u, tau_r = control

        velocity = np.array([u, v, r], dtype=float)
        kinematics = self._rotation_matrix(psi) @ velocity
        control_vector = np.array([tau_u, 0.0, tau_r], dtype=float)
        generalized_force = (
            control_vector
            + disturbance_vector
            - self._coriolis_vector(velocity)
            - self._damping_vector(velocity)
        )
        accelerations = self.inverse_mass_matrix @ generalized_force

        return np.concatenate([kinematics, accelerations])

    def step(
        self,
        state: np.ndarray,
        control: np.ndarray,
        dt: float,
        disturbance: np.ndarray | None = None,
    ) -> np.ndarray:
        state = self._validate_state(state)
        return state + float(dt) * self.dynamics(state, control, disturbance)
