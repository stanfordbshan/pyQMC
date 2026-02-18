# pyQMC Developer Manual

## Design goals
- Keep backend logic independent from GUI and transport concerns.
- Prioritize readability and educational clarity over optimization.

## Package layout
- `src/pyqmc/core`: shared backend config/result/stat utilities.
- `src/pyqmc/vmc`: VMC-specific model, sampler, and solver.
- `src/pyqmc/dmc`: reserved for future DMC module.
- `src/pyqmc/api`: FastAPI layer exposing backend functionality.
- `src/pyqmc/gui`: pywebview host process and frontend launcher.
- `src/pyqmc/gui/assets`: static frontend assets.

## Phase 1 implementation
- `pyqmc.vmc.harmonic_oscillator.HarmonicOscillator1D` defines model equations.
- `pyqmc.vmc.metropolis.sample_chain` performs random-walk Metropolis sampling.
- `pyqmc.vmc.solver.run_vmc_harmonic_oscillator` computes energy estimate and summary.
- `pyqmc.cli` exposes `pyqmc vmc-ho` command.

## Phase 2 implementation
- `pyqmc.api.api.create_app` builds the FastAPI application.
- `pyqmc.api.service` maps API requests to backend simulation calls.
- `pyqmc.api.models` defines request/response schemas.
- `pyqmc.api.api_server` runs uvicorn and is reused by `pyqmc serve-api`.
- `pyqmc.gui.app.launch_gui` starts pywebview and either:
  - launches an embedded local API process, or
  - connects to an external API URL.
- `src/pyqmc/gui/assets/*` contains UI HTML/CSS/JS and no backend logic.

## Separation of concerns
- `core`, `vmc`, `dmc` must remain free of web framework and GUI dependencies.
- `api` should only adapt transport (HTTP) to backend service calls.
- `gui` should only manage rendering and API communication.

## Testing (Phase 3)
- Unit tests live in `tests/unit` and cover:
  - config validation
  - statistical helpers
  - result serialization
  - harmonic oscillator equations
  - Metropolis sampler behavior
  - VMC solver outputs
- Integration tests live in `tests/integration` and cover:
  - CLI invocation and JSON output
  - API routes via in-process FastAPI `TestClient`
- Run full suite:
```bash
pytest
```

## Coding conventions
- Favor explicit function signatures and small modules.
- Add docstrings to all public functions/classes.
- Add comments only where logic is non-obvious.
