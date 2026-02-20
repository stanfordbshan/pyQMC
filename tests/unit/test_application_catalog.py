"""Unit tests for application catalog use-cases."""

from __future__ import annotations

from pyqmc.application.catalog import get_available_methods, get_available_systems


def test_get_available_methods_shape() -> None:
    methods = get_available_methods()

    assert methods
    first = methods[0]
    assert first["id"] == "vmc_metropolis"
    assert first["systems"] == ["harmonic_oscillator_1d"]


def test_get_available_systems_shape() -> None:
    systems = get_available_systems()

    assert systems
    first = systems[0]
    assert first["id"] == "harmonic_oscillator_1d"
    assert first["dimension"] == "1D"
