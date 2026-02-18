"""Pydantic models for API requests and responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class VmcHarmonicOscillatorRequest(BaseModel):
    """Input payload for VMC on the 1D harmonic oscillator."""

    n_steps: int = Field(default=20_000, gt=0)
    burn_in: int = Field(default=2_000, ge=0)
    step_size: float = Field(default=1.0, gt=0)
    alpha: float = Field(default=1.0, gt=0)
    initial_position: float = 0.0
    seed: int | None = 12345

    @model_validator(mode="after")
    def validate_burn_in(self) -> "VmcHarmonicOscillatorRequest":
        """Ensure burn-in is smaller than total steps."""
        if self.burn_in >= self.n_steps:
            raise ValueError("burn_in must be smaller than n_steps")
        return self


class SimulationResultResponse(BaseModel):
    """Serialized simulation summary returned by API endpoints."""

    method: str
    system: str
    n_samples: int
    mean_energy: float
    standard_error: float
    acceptance_ratio: float
    parameters: dict[str, Any]
    metadata: dict[str, Any]


class MethodInfo(BaseModel):
    """QMC method metadata for discovery endpoints."""

    id: str
    name: str
    description: str
    systems: list[str]


class SystemInfo(BaseModel):
    """System metadata for discovery endpoints."""

    id: str
    name: str
    dimension: str
    notes: str


class VmcHarmonicOscillatorBenchmarkRequest(BaseModel):
    """Input payload for benchmark suite execution."""

    n_steps: int = Field(default=30_000, gt=0)
    burn_in: int = Field(default=3_000, ge=0)
    step_size: float = Field(default=1.0, gt=0)
    initial_position: float = 0.0
    seed: int | None = 12345

    @model_validator(mode="after")
    def validate_burn_in(self) -> "VmcHarmonicOscillatorBenchmarkRequest":
        """Ensure burn-in is smaller than total steps."""
        if self.burn_in >= self.n_steps:
            raise ValueError("burn_in must be smaller than n_steps")
        return self


class BenchmarkCaseResponse(BaseModel):
    """One benchmark case result returned by API."""

    case_id: str
    description: str
    alpha: float
    reference_energy: float
    measured_energy: float
    standard_error: float
    abs_error: float
    tolerance: float
    passed: bool
    acceptance_ratio: float
    n_samples: int
    reference_source: str


class BenchmarkSuiteResponse(BaseModel):
    """Benchmark suite response payload."""

    suite_name: str
    method: str
    system: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    all_passed: bool
    cases: list[BenchmarkCaseResponse]
