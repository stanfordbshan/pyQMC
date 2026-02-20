"""Application/use-case layer for transport-agnostic orchestration.

This package provides stable backend entry points used by CLI, GUI, and API.
"""

from .catalog import get_available_methods, get_available_systems
from .vmc import (
    run_vmc_harmonic_oscillator_benchmark_use_case,
    run_vmc_harmonic_oscillator_use_case,
)

__all__ = [
    "get_available_methods",
    "get_available_systems",
    "run_vmc_harmonic_oscillator_benchmark_use_case",
    "run_vmc_harmonic_oscillator_use_case",
]
