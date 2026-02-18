"""Public VMC runners used by CLI/API layers."""

from pyqmc.core.config import SimulationConfig
from pyqmc.core.results import SimulationResult
from pyqmc.core.stats import mean, standard_error
from pyqmc.vmc.harmonic_oscillator import HarmonicOscillator1D
from pyqmc.vmc.metropolis import sample_chain


def run_vmc_harmonic_oscillator(config: SimulationConfig) -> SimulationResult:
    """Run educational VMC on the 1D harmonic oscillator.

    The exact ground-state energy is 0.5 in these units; this provides an
    immediate correctness check for students.
    """
    config.validate()

    system = HarmonicOscillator1D()
    trace = sample_chain(system, config)

    if not trace.local_energies:
        raise RuntimeError("no samples collected; check n_steps and burn_in")

    return SimulationResult(
        method="VMC (Metropolis)",
        system=system.name,
        n_samples=len(trace.local_energies),
        mean_energy=mean(trace.local_energies),
        standard_error=standard_error(trace.local_energies),
        acceptance_ratio=trace.acceptance_ratio,
        parameters={
            "alpha": config.alpha,
            "n_steps": config.n_steps,
            "burn_in": config.burn_in,
            "step_size": config.step_size,
            "initial_position": config.initial_position,
            "seed": config.seed,
        },
        metadata={
            "exact_ground_state_energy": 0.5,
            "notes": "Use alpha near 1.0 for best agreement in this simple trial family.",
        },
    )
