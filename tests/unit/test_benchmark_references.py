"""Unit tests for analytic benchmark reference formulas."""

from __future__ import annotations

import pytest

from pyqmc.benchmarks.references import (
    harmonic_oscillator_exact_ground_state_energy,
    harmonic_oscillator_variational_energy,
)


def test_exact_ground_state_energy_constant() -> None:
    assert harmonic_oscillator_exact_ground_state_energy() == pytest.approx(0.5)


def test_variational_energy_formula_known_values() -> None:
    assert harmonic_oscillator_variational_energy(1.0) == pytest.approx(0.5)
    assert harmonic_oscillator_variational_energy(0.8) == pytest.approx(0.5125)
    assert harmonic_oscillator_variational_energy(1.2) == pytest.approx(0.5083333333333333)


def test_variational_energy_rejects_nonpositive_alpha() -> None:
    with pytest.raises(ValueError, match="alpha must be positive"):
        harmonic_oscillator_variational_energy(0.0)
