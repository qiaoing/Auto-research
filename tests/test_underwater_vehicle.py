import numpy as np

from src.dynamics.underwater_vehicle import PlanarUnderwaterVehicle3DOF


def _expected_coupled_dynamics(
    state: np.ndarray,
    control: np.ndarray,
    mass_u: float,
    mass_v: float,
    inertia_r: float,
    linear_damping: tuple[float, float, float],
    quadratic_damping: tuple[float, float, float],
) -> np.ndarray:
    x, y, psi, u, v, r = state
    _ = (x, y)
    tau_u, tau_r = control

    rotation = np.array(
        [
            [np.cos(psi), -np.sin(psi), 0.0],
            [np.sin(psi), np.cos(psi), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    kinematics = rotation @ np.array([u, v, r], dtype=float)

    linear = np.asarray(linear_damping, dtype=float)
    quadratic = np.asarray(quadratic_damping, dtype=float)
    velocity = np.array([u, v, r], dtype=float)
    damping = linear * velocity + quadratic * np.abs(velocity) * velocity
    coriolis = np.array(
        [
            -mass_v * v * r,
            mass_u * u * r,
            (mass_v - mass_u) * u * v,
        ],
        dtype=float,
    )
    tau = np.array([tau_u, 0.0, tau_r], dtype=float)
    acceleration = np.array(
        [
            (tau[0] - coriolis[0] - damping[0]) / mass_u,
            (tau[1] - coriolis[1] - damping[1]) / mass_v,
            (tau[2] - coriolis[2] - damping[2]) / inertia_r,
        ],
        dtype=float,
    )

    return np.concatenate([kinematics, acceleration])


def test_dynamics_shape():
    model = PlanarUnderwaterVehicle3DOF()
    state = np.zeros(6)
    control = np.zeros(2)
    dx = model.dynamics(state, control)
    assert dx.shape == (6,)


def test_step_shape():
    model = PlanarUnderwaterVehicle3DOF()
    state = np.zeros(6)
    control = np.zeros(2)
    next_state = model.step(state, control, 0.1)
    assert next_state.shape == (6,)


def test_zero_control_and_zero_velocity_produce_no_acceleration():
    model = PlanarUnderwaterVehicle3DOF()
    state = np.array([3.0, -1.0, 0.7, 0.0, 0.0, 0.0], dtype=float)
    control = np.zeros(2)

    state_derivative = model.dynamics(state, control)

    np.testing.assert_allclose(state_derivative, np.zeros(6))


def test_dynamics_matches_coupled_reference_model():
    mass_u = 12.0
    mass_v = 15.0
    inertia_r = 4.0
    linear_damping = (5.0, 6.0, 1.5)
    quadratic_damping = (1.0, 1.2, 0.3)
    model = PlanarUnderwaterVehicle3DOF(
        mass_u=mass_u,
        mass_v=mass_v,
        inertia_r=inertia_r,
        linear_damping=linear_damping,
        quadratic_damping=quadratic_damping,
    )
    state = np.array([2.0, -1.0, 0.4, 1.5, -0.4, 0.6], dtype=float)
    control = np.array([7.0, -0.8], dtype=float)

    expected = _expected_coupled_dynamics(
        state=state,
        control=control,
        mass_u=mass_u,
        mass_v=mass_v,
        inertia_r=inertia_r,
        linear_damping=linear_damping,
        quadratic_damping=quadratic_damping,
    )

    np.testing.assert_allclose(model.dynamics(state, control), expected)


def test_dynamics_are_deterministic_for_fixed_inputs():
    model = PlanarUnderwaterVehicle3DOF()
    state = np.array([0.5, -0.2, -0.3, 0.7, 0.1, -0.2], dtype=float)
    control = np.array([1.3, 0.4], dtype=float)
    disturbance = np.array([0.2, -0.1, 0.05], dtype=float)

    first = model.dynamics(state, control, disturbance=disturbance)
    second = model.dynamics(state, control, disturbance=disturbance)

    np.testing.assert_allclose(first, second)


def test_step_updates_yaw_angle_with_nonzero_yaw_rate():
    model = PlanarUnderwaterVehicle3DOF()
    state = np.array([0.0, 0.0, 0.25, 0.0, 0.0, 0.6], dtype=float)
    control = np.zeros(2)
    dt = 0.2

    next_state = model.step(state, control, dt)

    assert next_state[2] == state[2] + dt * state[5]
