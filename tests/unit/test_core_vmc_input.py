"""Unit tests for shared VMC payload/config mapping helpers."""

from __future__ import annotations

import pytest

from pyqmc.core.vmc_input import (
    DEFAULT_VMC_N_STEPS,
    build_vmc_harmonic_oscillator_config,
    build_vmc_harmonic_oscillator_config_from_mapping,
)


def test_build_vmc_config_from_typed_values() -> None:
    config = build_vmc_harmonic_oscillator_config(
        n_steps=2000,
        burn_in=500,
        step_size=1.0,
        alpha=0.95,
        initial_position=0.0,
        seed=7,
    )

    assert config.n_steps == 2000
    assert config.burn_in == 500
    assert config.alpha == pytest.approx(0.95)


def test_build_vmc_config_from_mapping_with_defaults() -> None:
    config = build_vmc_harmonic_oscillator_config_from_mapping({})

    assert config.n_steps == DEFAULT_VMC_N_STEPS
    assert config.burn_in < config.n_steps


def test_build_vmc_config_from_mapping_rejects_bad_payload_type() -> None:
    with pytest.raises(ValueError, match="payload must be a JSON object"):
        build_vmc_harmonic_oscillator_config_from_mapping("invalid")  # type: ignore[arg-type]


def test_build_vmc_config_from_mapping_rejects_bad_numeric_type() -> None:
    with pytest.raises(ValueError, match="n_steps must be an integer"):
        build_vmc_harmonic_oscillator_config_from_mapping({"n_steps": "abc"})


def test_build_vmc_config_from_mapping_allows_null_seed() -> None:
    config = build_vmc_harmonic_oscillator_config_from_mapping(
        {
            "n_steps": 2000,
            "burn_in": 500,
            "step_size": 1.0,
            "alpha": 1.0,
            "initial_position": 0.0,
            "seed": None,
        }
    )

    assert config.seed is None


def test_build_vmc_config_propagates_domain_validation_errors() -> None:
    with pytest.raises(ValueError, match="burn_in must be smaller than n_steps"):
        build_vmc_harmonic_oscillator_config(
            n_steps=100,
            burn_in=100,
            step_size=1.0,
            alpha=1.0,
            initial_position=0.0,
            seed=7,
        )
