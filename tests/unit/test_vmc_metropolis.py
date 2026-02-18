"""Unit tests for Metropolis sampling mechanics."""

from __future__ import annotations

import pytest

from pyqmc.core.config import SimulationConfig
from pyqmc.vmc.harmonic_oscillator import HarmonicOscillator1D
from pyqmc.vmc.metropolis import sample_chain


def test_sampling_is_deterministic_for_fixed_seed() -> None:
    system = HarmonicOscillator1D()
    config = SimulationConfig(n_steps=120, burn_in=20, step_size=0.8, alpha=0.9, seed=7)

    trace_a = sample_chain(system, config)
    trace_b = sample_chain(system, config)

    assert trace_a.positions == trace_b.positions
    assert trace_a.local_energies == trace_b.local_energies
    assert trace_a.accepted_steps == trace_b.accepted_steps
    assert trace_a.attempted_steps == trace_b.attempted_steps


def test_sampling_collects_expected_number_of_post_burnin_samples() -> None:
    system = HarmonicOscillator1D()
    config = SimulationConfig(n_steps=200, burn_in=50, step_size=1.0, alpha=1.0, seed=3)

    trace = sample_chain(system, config)

    assert len(trace.positions) == 150
    assert len(trace.local_energies) == 150
    assert trace.attempted_steps == 200
    assert 0.0 <= trace.acceptance_ratio <= 1.0


def test_acceptance_ratio_zero_when_no_attempts() -> None:
    from pyqmc.vmc.metropolis import MetropolisTrace

    trace = MetropolisTrace(
        positions=[],
        local_energies=[],
        accepted_steps=0,
        attempted_steps=0,
    )
    assert trace.acceptance_ratio == 0.0


@pytest.mark.parametrize("step_size", [0.1, 1.0, 3.0])
def test_acceptance_ratio_within_bounds(step_size: float) -> None:
    system = HarmonicOscillator1D()
    config = SimulationConfig(
        n_steps=300,
        burn_in=50,
        step_size=step_size,
        alpha=0.95,
        seed=1,
    )

    trace = sample_chain(system, config)
    assert 0.0 <= trace.acceptance_ratio <= 1.0
