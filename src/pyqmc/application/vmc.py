"""VMC application use-cases shared by API, GUI, and CLI layers."""

from __future__ import annotations

from pyqmc.benchmarks.vmc_harmonic_oscillator import (
    BenchmarkSuiteResult,
    run_vmc_harmonic_oscillator_benchmarks,
)
from pyqmc.core.results import SimulationResult
from pyqmc.core.vmc_input import build_vmc_harmonic_oscillator_config
from pyqmc.vmc.solver import run_vmc_harmonic_oscillator


def run_vmc_harmonic_oscillator_use_case(
    *,
    n_steps: int,
    burn_in: int,
    step_size: float,
    alpha: float,
    initial_position: float,
    seed: int | None,
) -> SimulationResult:
    """Run one VMC simulation using transport-agnostic primitive arguments.

    Transport layers (HTTP, GUI bridge, CLI) should pass plain values here,
    allowing backend evolution without coupling to transport-specific schemas.
    """
    config = build_vmc_harmonic_oscillator_config(
        n_steps=n_steps,
        burn_in=burn_in,
        step_size=step_size,
        alpha=alpha,
        initial_position=initial_position,
        seed=seed,
    )
    return run_vmc_harmonic_oscillator(config)


def run_vmc_harmonic_oscillator_benchmark_use_case(
    *,
    n_steps: int,
    burn_in: int,
    step_size: float,
    initial_position: float,
    seed: int | None,
) -> BenchmarkSuiteResult:
    """Run benchmark suite with transport-agnostic primitive arguments."""
    return run_vmc_harmonic_oscillator_benchmarks(
        n_steps=n_steps,
        burn_in=burn_in,
        step_size=step_size,
        initial_position=initial_position,
        seed=seed,
    )
