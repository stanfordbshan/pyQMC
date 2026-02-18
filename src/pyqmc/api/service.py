"""Thin service layer used by API routes.

This module keeps route handlers small and delegates heavy lifting to backend
modules in `pyqmc.core` and method-specific packages.
"""

from __future__ import annotations

from pyqmc.core.config import SimulationConfig
from pyqmc.core.results import SimulationResult
from pyqmc.vmc.solver import run_vmc_harmonic_oscillator as run_vmc_ho_solver

from .models import MethodInfo, SystemInfo, VmcHarmonicOscillatorRequest


def list_methods() -> list[MethodInfo]:
    """Return currently available QMC methods in this educational build."""
    return [
        MethodInfo(
            id="vmc_metropolis",
            name="Variational Monte Carlo (Metropolis)",
            description="Random-walk Metropolis sampling of |psi_T|^2.",
            systems=["harmonic_oscillator_1d"],
        )
    ]


def list_systems() -> list[SystemInfo]:
    """Return currently available physical systems."""
    return [
        SystemInfo(
            id="harmonic_oscillator_1d",
            name="1D Harmonic Oscillator",
            dimension="1D",
            notes="Educational baseline with exact ground-state energy E0 = 0.5.",
        )
    ]


def run_vmc_harmonic_oscillator(
    request: VmcHarmonicOscillatorRequest,
) -> SimulationResult:
    """Execute the backend VMC solver for the requested configuration."""
    config = SimulationConfig(
        n_steps=request.n_steps,
        burn_in=request.burn_in,
        step_size=request.step_size,
        alpha=request.alpha,
        initial_position=request.initial_position,
        seed=request.seed,
    )

    return run_vmc_ho_solver(config)
