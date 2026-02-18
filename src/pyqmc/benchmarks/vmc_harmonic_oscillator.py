"""Benchmark runner for VMC on the 1D harmonic oscillator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pyqmc.core.config import SimulationConfig
from pyqmc.vmc.solver import run_vmc_harmonic_oscillator

from .references import (
    harmonic_oscillator_exact_ground_state_energy,
    harmonic_oscillator_variational_energy,
)


@dataclass(frozen=True)
class BenchmarkCase:
    """Definition of one benchmark target."""

    case_id: str
    description: str
    alpha: float
    reference_energy: float
    tolerance: float
    reference_source: str


@dataclass(frozen=True)
class BenchmarkCaseResult:
    """Outcome for one benchmark case."""

    case_id: str
    description: str
    alpha: float
    reference_energy: float
    measured_energy: float
    standard_error: float
    abs_error: float
    tolerance: float
    passed: bool
    acceptance_ratio: float
    n_samples: int
    reference_source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "alpha": self.alpha,
            "reference_energy": self.reference_energy,
            "measured_energy": self.measured_energy,
            "standard_error": self.standard_error,
            "abs_error": self.abs_error,
            "tolerance": self.tolerance,
            "passed": self.passed,
            "acceptance_ratio": self.acceptance_ratio,
            "n_samples": self.n_samples,
            "reference_source": self.reference_source,
        }


@dataclass(frozen=True)
class BenchmarkSuiteResult:
    """Summary for the benchmark suite."""

    suite_name: str
    method: str
    system: str
    cases: list[BenchmarkCaseResult] = field(default_factory=list)

    @property
    def total_cases(self) -> int:
        return len(self.cases)

    @property
    def passed_cases(self) -> int:
        return sum(1 for case in self.cases if case.passed)

    @property
    def failed_cases(self) -> int:
        return self.total_cases - self.passed_cases

    @property
    def all_passed(self) -> bool:
        return self.failed_cases == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "method": self.method,
            "system": self.system,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "all_passed": self.all_passed,
            "cases": [case.to_dict() for case in self.cases],
        }

    def to_pretty_text(self) -> str:
        status = "PASS" if self.all_passed else "FAIL"
        lines = [
            f"Benchmark suite: {self.suite_name}",
            f"Method: {self.method}",
            f"System: {self.system}",
            f"Overall: {status} ({self.passed_cases}/{self.total_cases} cases passed)",
        ]

        for case in self.cases:
            case_status = "PASS" if case.passed else "FAIL"
            lines.append(
                " - "
                f"[{case_status}] {case.case_id}: measured={case.measured_energy:.8f}, "
                f"reference={case.reference_energy:.8f}, "
                f"|error|={case.abs_error:.8f}, tol={case.tolerance:.8f}, "
                f"stderr={case.standard_error:.8f}"
            )

        return "\n".join(lines)


def _default_cases() -> list[BenchmarkCase]:
    """Return benchmark definitions with analytic/literature-backed references."""
    exact_source = (
        "Exact harmonic oscillator ground-state energy E0 = 1/2 in reduced units "
        "(standard quantum mechanics result)."
    )
    variational_source = (
        "Gaussian trial variational energy E(alpha) = 1/4(alpha + 1/alpha) "
        "for psi_T(x;alpha)=exp(-alpha x^2/2)."
    )

    return [
        BenchmarkCase(
            case_id="ho_exact_alpha_1.0",
            description="Exact-energy check with optimal alpha=1.0",
            alpha=1.0,
            reference_energy=harmonic_oscillator_exact_ground_state_energy(),
            tolerance=1e-12,
            reference_source=exact_source,
        ),
        BenchmarkCase(
            case_id="ho_variational_alpha_0.8",
            description="Variational reference check with alpha=0.8",
            alpha=0.8,
            reference_energy=harmonic_oscillator_variational_energy(0.8),
            tolerance=0.02,
            reference_source=variational_source,
        ),
        BenchmarkCase(
            case_id="ho_variational_alpha_1.2",
            description="Variational reference check with alpha=1.2",
            alpha=1.2,
            reference_energy=harmonic_oscillator_variational_energy(1.2),
            tolerance=0.02,
            reference_source=variational_source,
        ),
    ]


def run_vmc_harmonic_oscillator_benchmarks(
    n_steps: int = 30_000,
    burn_in: int = 3_000,
    step_size: float = 1.0,
    initial_position: float = 0.0,
    seed: int | None = 12345,
) -> BenchmarkSuiteResult:
    """Run built-in VMC benchmarks and compare against references.

    The benchmark cases intentionally keep scope small and transparent for
    educational use.
    """
    cases = _default_cases()
    results: list[BenchmarkCaseResult] = []

    for index, case in enumerate(cases):
        case_seed = None if seed is None else seed + index
        config = SimulationConfig(
            n_steps=n_steps,
            burn_in=burn_in,
            step_size=step_size,
            alpha=case.alpha,
            initial_position=initial_position,
            seed=case_seed,
        )
        simulation = run_vmc_harmonic_oscillator(config)

        abs_error = abs(simulation.mean_energy - case.reference_energy)
        results.append(
            BenchmarkCaseResult(
                case_id=case.case_id,
                description=case.description,
                alpha=case.alpha,
                reference_energy=case.reference_energy,
                measured_energy=simulation.mean_energy,
                standard_error=simulation.standard_error,
                abs_error=abs_error,
                tolerance=case.tolerance,
                passed=abs_error <= case.tolerance,
                acceptance_ratio=simulation.acceptance_ratio,
                n_samples=simulation.n_samples,
                reference_source=case.reference_source,
            )
        )

    return BenchmarkSuiteResult(
        suite_name="vmc_harmonic_oscillator_reference_suite",
        method="VMC (Metropolis)",
        system="harmonic_oscillator_1d",
        cases=results,
    )
