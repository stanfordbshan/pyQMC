"""Unit tests for pywebview local compute bridge."""

from __future__ import annotations

import pytest

from pyqmc.gui.app import LocalComputeBridge


def test_local_bridge_runs_vmc_without_http() -> None:
    bridge = LocalComputeBridge()
    payload = {
        "n_steps": 2000,
        "burn_in": 500,
        "step_size": 1.0,
        "alpha": 1.0,
        "initial_position": 0.0,
        "seed": 7,
    }

    result = bridge.run_vmc_harmonic_oscillator(payload)

    assert result["method"] == "VMC (Metropolis)"
    assert result["system"] == "harmonic_oscillator_1d"
    assert result["n_samples"] == 1500
    assert result["mean_energy"] == pytest.approx(0.5)


def test_local_bridge_rejects_invalid_payload_type() -> None:
    bridge = LocalComputeBridge()

    with pytest.raises(ValueError, match="payload must be a JSON object"):
        bridge.run_vmc_harmonic_oscillator(payload="invalid")  # type: ignore[arg-type]


def test_local_bridge_propagates_config_validation_errors() -> None:
    bridge = LocalComputeBridge()
    payload = {
        "n_steps": 100,
        "burn_in": 100,
        "step_size": 1.0,
        "alpha": 1.0,
        "initial_position": 0.0,
        "seed": 7,
    }

    with pytest.raises(ValueError, match="burn_in must be smaller than n_steps"):
        bridge.run_vmc_harmonic_oscillator(payload)
