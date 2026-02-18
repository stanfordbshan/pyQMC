"""Unit tests for basic Monte Carlo statistics helpers."""

from __future__ import annotations

import math

import pytest

from pyqmc.core.stats import mean, sample_variance, standard_error


def test_mean_and_variance_known_values() -> None:
    values = [1.0, 2.0, 3.0, 4.0]

    assert mean(values) == pytest.approx(2.5)
    assert sample_variance(values) == pytest.approx(5.0 / 3.0)


def test_sample_variance_for_short_sequences() -> None:
    assert sample_variance([]) == 0.0
    assert sample_variance([42.0]) == 0.0


def test_standard_error_known_values() -> None:
    values = [1.0, 2.0, 3.0, 4.0]
    expected = math.sqrt((5.0 / 3.0) / 4.0)
    assert standard_error(values) == pytest.approx(expected)


def test_standard_error_single_value_is_zero() -> None:
    assert standard_error([2.0]) == 0.0


def test_mean_and_standard_error_raise_on_empty_input() -> None:
    with pytest.raises(ValueError, match="mean requires at least one value"):
        mean([])

    with pytest.raises(ValueError, match="standard_error requires at least one value"):
        standard_error([])
