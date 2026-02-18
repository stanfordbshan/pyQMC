"""Unit tests for harmonic oscillator model equations."""

from __future__ import annotations

import pytest

from pyqmc.vmc.harmonic_oscillator import HarmonicOscillator1D


def test_log_probability_matches_wavefunction_squared() -> None:
    system = HarmonicOscillator1D()
    x = 1.25
    alpha = 0.8

    assert system.log_probability_density(x, alpha) == pytest.approx(
        2.0 * system.log_trial_wavefunction(x, alpha)
    )


@pytest.mark.parametrize("x", [-2.0, -0.2, 0.0, 0.3, 1.7])
def test_local_energy_is_constant_for_alpha_one(x: float) -> None:
    system = HarmonicOscillator1D()

    assert system.local_energy(x, alpha=1.0) == pytest.approx(0.5)


def test_local_energy_matches_analytic_expression() -> None:
    system = HarmonicOscillator1D()
    x = 1.1
    alpha = 0.9

    expected = 0.5 * alpha + 0.5 * (1.0 - alpha * alpha) * x * x
    assert system.local_energy(x, alpha) == pytest.approx(expected)
