"""Unit tests for simulation configuration validation."""

from __future__ import annotations

import pytest

from pyqmc.core.config import SimulationConfig


def test_validate_accepts_valid_configuration() -> None:
    config = SimulationConfig(
        n_steps=100,
        burn_in=10,
        step_size=0.5,
        alpha=1.2,
        initial_position=0.0,
        seed=42,
    )

    config.validate()


@pytest.mark.parametrize(
    ("overrides", "error_fragment"),
    [
        ({"n_steps": 0}, "n_steps must be positive"),
        ({"burn_in": -1}, "burn_in cannot be negative"),
        ({"n_steps": 10, "burn_in": 10}, "burn_in must be smaller than n_steps"),
        ({"step_size": 0.0}, "step_size must be positive"),
        ({"alpha": 0.0}, "alpha must be positive"),
    ],
)
def test_validate_rejects_invalid_values(
    overrides: dict[str, float | int],
    error_fragment: str,
) -> None:
    kwargs = {
        "n_steps": 100,
        "burn_in": 10,
        "step_size": 0.5,
        "alpha": 1.0,
        "initial_position": 0.0,
        "seed": 1,
    }
    kwargs.update(overrides)
    config = SimulationConfig(**kwargs)

    with pytest.raises(ValueError, match=error_fragment):
        config.validate()
