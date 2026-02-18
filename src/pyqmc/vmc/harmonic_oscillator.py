"""1D quantum harmonic oscillator model for VMC examples.

Units are chosen as hbar = m = omega = 1.
"""


class HarmonicOscillator1D:
    """Simple analytic model used as a first educational VMC target."""

    name = "harmonic_oscillator_1d"

    def log_trial_wavefunction(self, x: float, alpha: float) -> float:
        """Return log(psi_T(x; alpha)) for psi_T = exp(-alpha * x^2 / 2)."""
        return -0.5 * alpha * x * x

    def log_probability_density(self, x: float, alpha: float) -> float:
        """Return log(|psi_T|^2), the distribution sampled by Metropolis."""
        return 2.0 * self.log_trial_wavefunction(x, alpha)

    def local_energy(self, x: float, alpha: float) -> float:
        """Return local energy E_L(x) = H psi_T / psi_T.

        For this trial wavefunction and units:
        E_L(x) = alpha / 2 + (1 - alpha^2) * x^2 / 2
        """
        return 0.5 * alpha + 0.5 * (1.0 - alpha * alpha) * x * x
