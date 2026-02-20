"""Shared VMC payload validation and `SimulationConfig` mapping helpers.

This module is intentionally used by both API and GUI layers to keep request
field semantics synchronized. Centralizing this conversion logic avoids subtle
behavior drift when one transport path evolves.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .config import SimulationConfig

# Keep one source of truth for default GUI/API simulation controls.
DEFAULT_VMC_N_STEPS = 20_000
DEFAULT_VMC_BURN_IN = 2_000
DEFAULT_VMC_STEP_SIZE = 1.0
DEFAULT_VMC_ALPHA = 1.0
DEFAULT_VMC_INITIAL_POSITION = 0.0
DEFAULT_VMC_SEED = 12345


def _parse_int(value: Any, field_name: str) -> int:
    """Parse and validate one integer-like value from external payloads."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


def _parse_float(value: Any, field_name: str) -> float:
    """Parse and validate one float-like value from external payloads."""
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number") from exc


def _parse_optional_int(value: Any, field_name: str) -> int | None:
    """Parse optional integer field where `None`/empty string means null."""
    if value in (None, ""):
        return None
    return _parse_int(value, field_name)


def build_vmc_harmonic_oscillator_config(
    *,
    n_steps: int = DEFAULT_VMC_N_STEPS,
    burn_in: int = DEFAULT_VMC_BURN_IN,
    step_size: float = DEFAULT_VMC_STEP_SIZE,
    alpha: float = DEFAULT_VMC_ALPHA,
    initial_position: float = DEFAULT_VMC_INITIAL_POSITION,
    seed: int | None = DEFAULT_VMC_SEED,
) -> SimulationConfig:
    """Build a validated `SimulationConfig` for VMC harmonic oscillator runs.

    This function is transport-agnostic and should be preferred whenever callers
    already have typed values (for example from Pydantic models).
    """
    config = SimulationConfig(
        n_steps=int(n_steps),
        burn_in=int(burn_in),
        step_size=float(step_size),
        alpha=float(alpha),
        initial_position=float(initial_position),
        seed=None if seed is None else int(seed),
    )
    config.validate()
    return config


def build_vmc_harmonic_oscillator_config_from_mapping(
    payload: Mapping[str, Any],
) -> SimulationConfig:
    """Build a validated `SimulationConfig` from raw JSON-like mapping input.

    This path is used by the GUI direct-compute bridge, where incoming values
    originate from browser form fields and are not strongly typed.
    """
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a JSON object")

    return build_vmc_harmonic_oscillator_config(
        n_steps=_parse_int(payload.get("n_steps", DEFAULT_VMC_N_STEPS), "n_steps"),
        burn_in=_parse_int(payload.get("burn_in", DEFAULT_VMC_BURN_IN), "burn_in"),
        step_size=_parse_float(
            payload.get("step_size", DEFAULT_VMC_STEP_SIZE),
            "step_size",
        ),
        alpha=_parse_float(payload.get("alpha", DEFAULT_VMC_ALPHA), "alpha"),
        initial_position=_parse_float(
            payload.get("initial_position", DEFAULT_VMC_INITIAL_POSITION),
            "initial_position",
        ),
        seed=_parse_optional_int(payload.get("seed", DEFAULT_VMC_SEED), "seed"),
    )
