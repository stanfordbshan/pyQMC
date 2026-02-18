"""Unit tests for public VMC solver API."""

from __future__ import annotations

import pytest

from pyqmc.core.config import SimulationConfig
from pyqmc.vmc.solver import run_vmc_harmonic_oscillator


def test_solver_returns_expected_summary_fields() -> None:
    config = SimulationConfig(n_steps=3000, burn_in=500, step_size=1.0, alpha=0.95, seed=7)

    result = run_vmc_harmonic_oscillator(config)

    assert result.method == "VMC (Metropolis)"
    assert result.system == "harmonic_oscillator_1d"
    assert result.n_samples == 2500
    assert 0.0 <= result.acceptance_ratio <= 1.0
    assert result.parameters["alpha"] == 0.95
    assert result.metadata["exact_ground_state_energy"] == 0.5


def test_solver_alpha_one_produces_exact_constant_local_energy() -> None:
    config = SimulationConfig(n_steps=1500, burn_in=500, step_size=1.0, alpha=1.0, seed=9)

    result = run_vmc_harmonic_oscillator(config)

    assert result.mean_energy == pytest.approx(0.5)
    assert result.standard_error == pytest.approx(0.0)


def test_solver_raises_for_invalid_config() -> None:
    invalid = SimulationConfig(n_steps=100, burn_in=100)

    with pytest.raises(ValueError, match="burn_in must be smaller than n_steps"):
        run_vmc_harmonic_oscillator(invalid)
