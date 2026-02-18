"""Unit tests for simulation result serialization utilities."""

from __future__ import annotations

from pyqmc.core.results import SimulationResult


def test_to_dict_returns_serializable_copy() -> None:
    result = SimulationResult(
        method="VMC",
        system="harmonic_oscillator_1d",
        n_samples=100,
        mean_energy=0.5,
        standard_error=0.01,
        acceptance_ratio=0.7,
        parameters={"alpha": 1.0},
        metadata={"exact_ground_state_energy": 0.5},
    )

    payload = result.to_dict()
    assert payload["method"] == "VMC"
    assert payload["parameters"] == {"alpha": 1.0}

    # Mutating the serialized dict must not affect the frozen dataclass internals.
    payload["parameters"]["alpha"] = 2.0
    assert result.parameters["alpha"] == 1.0


def test_pretty_text_contains_key_fields() -> None:
    result = SimulationResult(
        method="VMC",
        system="harmonic_oscillator_1d",
        n_samples=50,
        mean_energy=0.5,
        standard_error=0.0,
        acceptance_ratio=0.75,
    )

    text = result.to_pretty_text()
    assert "Method: VMC" in text
    assert "System: harmonic_oscillator_1d" in text
    assert "Samples: 50" in text
    assert "Mean energy: 0.50000000" in text
