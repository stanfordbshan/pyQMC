"""Configuration objects for simulations.

These objects are intentionally simple and explicit for educational use.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """Common controls for Monte Carlo simulations.

    Attributes:
        n_steps: Total Monte Carlo steps including burn-in.
        burn_in: Number of initial steps discarded before statistics.
        step_size: Proposal width for random-walk Metropolis.
        alpha: Trial-wavefunction variational parameter.
        initial_position: Initial particle coordinate.
        seed: Optional RNG seed for reproducibility.
    """

    n_steps: int = 20_000
    burn_in: int = 2_000
    step_size: float = 1.0
    alpha: float = 1.0
    initial_position: float = 0.0
    seed: int | None = 12345

    def validate(self) -> None:
        """Raise `ValueError` when configuration fields are invalid."""
        if self.n_steps <= 0:
            raise ValueError("n_steps must be positive")
        if self.burn_in < 0:
            raise ValueError("burn_in cannot be negative")
        if self.burn_in >= self.n_steps:
            raise ValueError("burn_in must be smaller than n_steps")
        if self.step_size <= 0:
            raise ValueError("step_size must be positive")
        if self.alpha <= 0:
            raise ValueError("alpha must be positive")
