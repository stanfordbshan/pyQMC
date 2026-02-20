"""Unit tests for application-level VMC use-cases."""

from __future__ import annotations

import pytest

from pyqmc.application.vmc import (
    run_vmc_harmonic_oscillator_benchmark_use_case,
    run_vmc_harmonic_oscillator_use_case,
)


def test_run_vmc_harmonic_oscillator_use_case_returns_expected_result() -> None:
    result = run_vmc_harmonic_oscillator_use_case(
        n_steps=3000,
        burn_in=500,
        step_size=1.0,
        alpha=0.95,
        initial_position=0.0,
        seed=7,
    )

    assert result.system == "harmonic_oscillator_1d"
    assert result.n_samples == 2500
    assert abs(result.mean_energy - 0.5) < 0.05


def test_run_vmc_harmonic_oscillator_use_case_validates_input() -> None:
    with pytest.raises(ValueError, match="burn_in must be smaller than n_steps"):
        run_vmc_harmonic_oscillator_use_case(
            n_steps=100,
            burn_in=100,
            step_size=1.0,
            alpha=1.0,
            initial_position=0.0,
            seed=7,
        )


def test_run_vmc_harmonic_oscillator_benchmark_use_case_runs() -> None:
    suite = run_vmc_harmonic_oscillator_benchmark_use_case(
        n_steps=6000,
        burn_in=1000,
        step_size=1.0,
        initial_position=0.0,
        seed=7,
    )

    assert suite.total_cases == 3
    assert suite.all_passed
