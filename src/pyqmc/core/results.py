"""Result models returned by backend computations."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SimulationResult:
    """Serializable result for one simulation run."""

    method: str
    system: str
    n_samples: int
    mean_energy: float
    standard_error: float
    acceptance_ratio: float
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for JSON/API responses."""
        return {
            "method": self.method,
            "system": self.system,
            "n_samples": self.n_samples,
            "mean_energy": self.mean_energy,
            "standard_error": self.standard_error,
            "acceptance_ratio": self.acceptance_ratio,
            "parameters": dict(self.parameters),
            "metadata": dict(self.metadata),
        }

    def to_pretty_text(self) -> str:
        """Return a compact multi-line summary for CLI output."""
        return (
            f"Method: {self.method}\n"
            f"System: {self.system}\n"
            f"Samples: {self.n_samples}\n"
            f"Mean energy: {self.mean_energy:.8f}\n"
            f"Standard error: {self.standard_error:.8f}\n"
            f"Acceptance ratio: {self.acceptance_ratio:.4f}"
        )
