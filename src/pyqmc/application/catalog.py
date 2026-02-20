"""Read-only application catalog use-cases.

These functions expose method/system metadata without coupling to HTTP schemas.
"""

from __future__ import annotations

from typing import Any


def get_available_methods() -> list[dict[str, Any]]:
    """Return available QMC methods for discovery UIs/transports."""
    return [
        {
            "id": "vmc_metropolis",
            "name": "Variational Monte Carlo (Metropolis)",
            "description": "Random-walk Metropolis sampling of |psi_T|^2.",
            "systems": ["harmonic_oscillator_1d"],
        }
    ]


def get_available_systems() -> list[dict[str, str]]:
    """Return available physical systems for discovery UIs/transports."""
    return [
        {
            "id": "harmonic_oscillator_1d",
            "name": "1D Harmonic Oscillator",
            "dimension": "1D",
            "notes": "Educational baseline with exact ground-state energy E0 = 0.5.",
        }
    ]
