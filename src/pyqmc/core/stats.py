"""Small statistical helpers for Monte Carlo estimators."""

import math
from collections.abc import Sequence


def mean(values: Sequence[float]) -> float:
    """Compute arithmetic mean.

    A tiny utility is used instead of NumPy so the educational baseline has
    minimal dependencies.
    """
    if not values:
        raise ValueError("mean requires at least one value")
    return sum(values) / len(values)


def sample_variance(values: Sequence[float]) -> float:
    """Compute unbiased sample variance (ddof=1)."""
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return sum((x - mu) ** 2 for x in values) / (len(values) - 1)


def standard_error(values: Sequence[float]) -> float:
    """Compute standard error of the mean."""
    if not values:
        raise ValueError("standard_error requires at least one value")
    if len(values) == 1:
        return 0.0
    return math.sqrt(sample_variance(values) / len(values))
