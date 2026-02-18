"""FastAPI app factory for pyQMC backend services."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pyqmc import __version__

from .models import (
    BenchmarkSuiteResponse,
    MethodInfo,
    SimulationResultResponse,
    SystemInfo,
    VmcHarmonicOscillatorBenchmarkRequest,
    VmcHarmonicOscillatorRequest,
)
from .service import (
    list_methods,
    list_systems,
    run_vmc_harmonic_oscillator,
    run_vmc_harmonic_oscillator_benchmark_suite,
)


def create_app() -> FastAPI:
    """Create and configure the pyQMC FastAPI app."""
    app = FastAPI(
        title="pyQMC API",
        version=__version__,
        description=(
            "Educational Quantum Monte Carlo API. "
            "This service exposes backend computations for CLI and GUI clients."
        ),
    )

    # This educational app allows broad CORS so local HTML/pywebview clients can
    # call the API without extra setup.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/methods", response_model=list[MethodInfo], tags=["catalog"])
    def methods() -> list[MethodInfo]:
        return list_methods()

    @app.get("/systems", response_model=list[SystemInfo], tags=["catalog"])
    def systems() -> list[SystemInfo]:
        return list_systems()

    @app.post(
        "/simulate/vmc/harmonic-oscillator",
        response_model=SimulationResultResponse,
        tags=["simulate"],
    )
    def simulate_vmc_harmonic_oscillator(
        payload: VmcHarmonicOscillatorRequest,
    ) -> SimulationResultResponse:
        result = run_vmc_harmonic_oscillator(payload)
        return SimulationResultResponse(**result.to_dict())

    @app.post(
        "/benchmark/vmc/harmonic-oscillator",
        response_model=BenchmarkSuiteResponse,
        tags=["benchmark"],
    )
    def benchmark_vmc_harmonic_oscillator(
        payload: VmcHarmonicOscillatorBenchmarkRequest,
    ) -> BenchmarkSuiteResponse:
        suite = run_vmc_harmonic_oscillator_benchmark_suite(payload)
        return BenchmarkSuiteResponse(**suite.to_dict())

    return app
