"""Unit tests for benchmark suite runner."""

from __future__ import annotations

from pyqmc.benchmarks.vmc_harmonic_oscillator import (
    run_vmc_harmonic_oscillator_benchmarks,
)


def test_benchmark_suite_structure_and_pass_status() -> None:
    suite = run_vmc_harmonic_oscillator_benchmarks(
        n_steps=12_000,
        burn_in=2_000,
        step_size=1.0,
        seed=7,
    )

    assert suite.suite_name == "vmc_harmonic_oscillator_reference_suite"
    assert suite.method == "VMC (Metropolis)"
    assert suite.system == "harmonic_oscillator_1d"

    assert suite.total_cases == 3
    assert suite.passed_cases == 3
    assert suite.failed_cases == 0
    assert suite.all_passed


def test_benchmark_case_fields_are_filled() -> None:
    suite = run_vmc_harmonic_oscillator_benchmarks(
        n_steps=6_000,
        burn_in=1_000,
        step_size=1.0,
        seed=5,
    )

    for case in suite.cases:
        assert case.case_id
        assert case.reference_source
        assert case.n_samples == 5_000
        assert 0.0 <= case.acceptance_ratio <= 1.0
        assert case.abs_error >= 0.0


def test_benchmark_serialization_contains_summary_fields() -> None:
    suite = run_vmc_harmonic_oscillator_benchmarks(
        n_steps=3_000,
        burn_in=500,
        seed=11,
    )

    payload = suite.to_dict()
    assert payload["total_cases"] == 3
    assert payload["passed_cases"] + payload["failed_cases"] == 3
    assert len(payload["cases"]) == 3
