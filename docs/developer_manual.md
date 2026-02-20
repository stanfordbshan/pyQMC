# pyQMC Developer Manual

## Design Goals
- Keep backend logic independent from GUI and transport layers.
- Prioritize educational clarity over optimization.
- Keep numerical behavior reproducible via explicit RNG seeds.

## Package Layout
- `src/pyqmc/core`: shared backend utilities (config, stats, result models)
- `src/pyqmc/vmc`: VMC method modules (model, sampler, solver)
- `src/pyqmc/dmc`: placeholder for future DMC implementation
- `src/pyqmc/benchmarks`: benchmark suite and reference formulas
- `src/pyqmc/api`: FastAPI transport layer
- `src/pyqmc/gui`: pywebview host and UI bootstrap
- `src/pyqmc/gui/assets`: static frontend assets (HTML/CSS/JS)

## Documentation Index
- API 中文开发详解：
  - `src/pyqmc/api/API_DEVELOPER_GUIDE_ZH.md`
- 基准参考说明：
  - `docs/benchmark_references.md`

## Layer Responsibilities
- `core` / `vmc` / `dmc`:
  - no FastAPI imports
  - no pywebview imports
  - pure simulation and numerical logic
- `api`:
  - pydantic request/response models
  - endpoint handlers that call backend services
- `gui`:
  - desktop window lifecycle
  - local direct-compute bridge (`pywebview` JS -> Python)
  - startup of embedded API process (optional fallback)
  - browser-side UI can talk to API endpoints when needed

## Command Entry Points
Primary CLI command:
- `pyqmc` (`src/pyqmc/cli.py`)

Subcommands:
- `pyqmc vmc-ho`
- `pyqmc serve-api`
- `pyqmc gui`
- `pyqmc benchmark`

GUI transport modes:
- `pyqmc gui --compute-mode auto` (default): direct local compute first, API fallback second
- `pyqmc gui --compute-mode direct`: direct local compute only
- `pyqmc gui --compute-mode api`: API-only transport

Dedicated wrappers:
- `pyqmc-api` -> `src/pyqmc/api/api_server.py`
- `pyqmc-gui` -> `src/pyqmc/gui/app.py`

## Benchmark System (Phase 4)
Modules:
- `src/pyqmc/benchmarks/references.py`
- `src/pyqmc/benchmarks/vmc_harmonic_oscillator.py`

Behavior:
- Runs reproducible VMC benchmark cases with fixed seeds.
- Compares measured energy to reference energy.
- Computes absolute error and pass/fail against tolerance.
- Produces both human-readable and JSON summaries.

Current cases:
- exact check at `alpha = 1.0`
- variational-reference checks at `alpha = 0.8` and `alpha = 1.2`

Reference details are documented in:
- `docs/benchmark_references.md`

## API Endpoints
Catalog/meta:
- `GET /health`
- `GET /methods`
- `GET /systems`

Simulation:
- `POST /simulate/vmc/harmonic-oscillator`

Benchmark:
- `POST /benchmark/vmc/harmonic-oscillator`

## Testing
Test layout:
- `tests/unit`: fast deterministic checks for formulas, stats, solver internals
- `tests/integration`: CLI and API integration checks

Run all tests:
```bash
pytest
```

## Extension Guide
To add a new physical system or method:
1. Add model/wavefunction/sampler logic under `src/pyqmc/<method>` or `src/pyqmc/core`.
2. Add a solver function returning `SimulationResult`.
3. Add CLI command wiring in `src/pyqmc/cli.py`.
4. Add API request/response models and route handlers in `src/pyqmc/api`.
5. Add benchmark references and cases in `src/pyqmc/benchmarks`.
6. Add unit + integration tests.
7. Update user/developer manuals.

## Coding Conventions
- Prefer explicit types and small focused functions.
- Add docstrings for public functions/classes.
- Add concise comments only where logic is non-obvious.
- Keep reproducibility controls (`seed`) visible at API and CLI boundaries.
