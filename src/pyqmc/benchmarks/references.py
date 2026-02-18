"""Reference energies and formulas used by benchmark checks."""

from __future__ import annotations


def harmonic_oscillator_exact_ground_state_energy() -> float:
    """Return exact E0 for 1D harmonic oscillator in units hbar = m = omega = 1."""
    return 0.5


def harmonic_oscillator_variational_energy(alpha: float) -> float:
    """Return analytic variational energy for Gaussian trial wavefunction.

    For psi_T(x; alpha) = exp(-alpha x^2 / 2), the expectation value is:

        E(alpha) = 1/4 * (alpha + 1/alpha)

    This provides an exact reference for validating VMC sample estimates.
    """
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    return 0.25 * (alpha + 1.0 / alpha)
