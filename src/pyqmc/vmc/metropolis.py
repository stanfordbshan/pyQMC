"""Random-walk Metropolis sampler for 1D VMC demonstrations."""

from dataclasses import dataclass
import math
import random

from pyqmc.core.config import SimulationConfig


@dataclass
class MetropolisTrace:
    """Raw samples produced by one Metropolis chain."""

    positions: list[float]
    local_energies: list[float]
    accepted_steps: int
    attempted_steps: int

    @property
    def acceptance_ratio(self) -> float:
        if self.attempted_steps == 0:
            return 0.0
        return self.accepted_steps / self.attempted_steps


def sample_chain(system: object, config: SimulationConfig) -> MetropolisTrace:
    """Run a single Metropolis chain.

    The `system` object is expected to expose:
    - log_probability_density(x, alpha)
    - local_energy(x, alpha)
    """
    rng = random.Random(config.seed)

    x = config.initial_position
    log_prob_x = system.log_probability_density(x, config.alpha)

    positions: list[float] = []
    local_energies: list[float] = []
    accepted = 0
    attempted = 0

    for step in range(config.n_steps):
        proposal = x + rng.uniform(-config.step_size, config.step_size)
        log_prob_proposal = system.log_probability_density(proposal, config.alpha)

        # Use a log test for numerical stability: accept if log(u) < delta_log_prob.
        log_accept_ratio = log_prob_proposal - log_prob_x
        if math.log(rng.random()) < log_accept_ratio:
            x = proposal
            log_prob_x = log_prob_proposal
            accepted += 1
        attempted += 1

        if step >= config.burn_in:
            positions.append(x)
            local_energies.append(system.local_energy(x, config.alpha))

    return MetropolisTrace(
        positions=positions,
        local_energies=local_energies,
        accepted_steps=accepted,
        attempted_steps=attempted,
    )
