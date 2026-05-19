import numpy as np

from src.dynamics.underwater_vehicle import PlanarUnderwaterVehicle3DOF


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
