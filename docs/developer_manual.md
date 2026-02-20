# pyQMC Developer Manual

## Design Goals
- Keep backend logic independent from GUI and transport layers.
- Prioritize educational clarity over optimization.
- Keep numerical behavior reproducible via explicit RNG seeds.

## Package Layout
- `src/pyqmc/core`: shared backend utilities (config, stats, result models)
  - includes shared transport-agnostic input mapping (`core/vmc_input.py`)
- `src/pyqmc/application`: transport-agnostic use-case orchestration layer
- `src/pyqmc/vmc`: VMC method modules (model, sampler, solver)
- `src/pyqmc/dmc`: placeholder for future DMC implementation
- `src/pyqmc/benchmarks`: benchmark suite and reference formulas
- `src/pyqmc/api`: FastAPI transport layer
- `src/pyqmc/gui`: pywebview host and UI bootstrap
- `src/pyqmc/gui/assets`: static frontend assets (HTML/CSS/JS)

## Repository File Tree
The tree below focuses on source and docs. Generated/cache folders (for example
`__pycache__`, `.pytest_cache`, `.git`) are omitted.

```text
pyQMC/
├── README.md
├── LICENSE
├── pyproject.toml
├── environment.yml
├── docs/
│   ├── user_manual.md
│   ├── developer_manual.md
│   └── benchmark_references.md
├── src/
│   └── pyqmc/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── stats.py
│       │   ├── results.py
│       │   └── vmc_input.py
│       ├── application/
│       │   ├── __init__.py
│       │   ├── catalog.py
│       │   └── vmc.py
│       ├── vmc/
│       │   ├── __init__.py
│       │   ├── harmonic_oscillator.py
│       │   ├── metropolis.py
│       │   └── solver.py
│       ├── dmc/
│       │   └── __init__.py
│       ├── benchmarks/
│       │   ├── __init__.py
│       │   ├── references.py
│       │   └── vmc_harmonic_oscillator.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── api.py
│       │   ├── api_server.py
│       │   ├── models.py
│       │   └── API_DEVELOPER_GUIDE_ZH.md
│       └── gui/
│           ├── __init__.py
│           ├── __main__.py
│           ├── app.py
│           ├── GUI_DEVELOPER_NOTE_ZH.md
│           └── assets/
│               ├── index.html
│               ├── app.js
│               ├── styles.css
│               └── ho_primer.svg
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_core_config.py
    │   ├── test_core_stats.py
    │   ├── test_core_results.py
    │   ├── test_core_vmc_input.py
    │   ├── test_application_vmc.py
    │   ├── test_application_catalog.py
    │   ├── test_vmc_harmonic_oscillator.py
    │   ├── test_vmc_metropolis.py
    │   ├── test_vmc_solver.py
    │   ├── test_gui_local_compute_bridge.py
    │   ├── test_benchmark_references.py
    │   └── test_benchmark_vmc_harmonic_oscillator.py
    └── integration/
        ├── test_cli.py
        └── test_api.py
```

## Structure Philosophy
- Backend-first core:
  - Numerical logic lives in `core`, `vmc`, `dmc`.
  - Physics code does not import GUI/web framework code.
- Use-case/application layer:
  - `application` coordinates backend flows for all transports.
  - Avoids duplicating orchestration logic in API/GUI/CLI adapters.
- Transport separation:
  - `api` is an adapter layer (HTTP, schemas, route wiring), not business logic.
  - `gui` is a presentation/orchestration layer (pywebview window + JS bridge).
- Shared mapping to prevent drift:
  - `core/vmc_input.py` centralizes payload defaults and mapping to
    `SimulationConfig`, reused by API and GUI direct mode.
- Method-oriented growth path:
  - Add new QMC categories as top-level method packages (`vmc`, `dmc`, future
    modules) instead of mixing all logic into one file tree.
- Test pyramid by intent:
  - `tests/unit` checks formulas/mapping/components.
  - `tests/integration` checks user-visible contracts (CLI/API).
- Documentation close to code:
  - High-level manuals live in `docs/`.
  - Deep domain guides can live near modules (for example API/GUI Chinese
    developer notes), making maintenance easier during refactors.

## Detailed Architecture Design and Why It Matters
This section describes the repository as an explicit layered architecture, not
just a folder grouping. The key objective is to separate computational science
logic from transport/presentation details while still supporting desktop and
service workflows from one codebase.

### 1. Layered file-tree design
The structure under `src/pyqmc` is intentionally split by responsibility:

- Domain and numerical core:
  - `core/`: shared primitives, configuration objects, input mapping, stats,
    and result containers.
  - `vmc/`, `dmc/`: method-specific scientific implementations.
- Application/use-case layer:
  - `application/`: transport-agnostic orchestration. Coordinates domain
    modules to deliver complete user-facing operations.
- Adapter layers:
  - `api/`: HTTP adapter (FastAPI routes, request/response schemas, server
    startup).
  - `gui/`: desktop adapter (pywebview lifecycle, JavaScript bridge, embedded
    API fallback bootstrap).
- Cross-cutting validation:
  - `core/vmc_input.py`: shared payload defaults and mapping logic used by
    both API and GUI bridge to avoid drift.

This file-tree design ensures each layer has one primary reason to change:
- Domain methods change for physics/numerics.
- Application changes for use-case orchestration.
- Adapters change for protocol/UI/runtime concerns.

### 2. Dependency direction rules
The architecture follows strict inward dependency flow:

- Allowed direction:
  - `api` -> `application` -> (`core`, `vmc`, `dmc`, `benchmarks`)
  - `gui` -> `application` -> (`core`, `vmc`, `dmc`, `benchmarks`)
  - `cli` -> `application` -> (`core`, `vmc`, `dmc`, `benchmarks`)
- Not allowed:
  - `core` importing `api`/`gui`
  - `vmc` importing FastAPI/pywebview
  - `application` depending on HTTP request models or GUI window objects

Practical effect:
- Scientific code can run in tests, CLI, notebook, GUI direct mode, or remote
  API mode without rewrite.
- API schema evolution does not force edits to solver internals.
- GUI layout changes do not risk numerical behavior regression.

### 3. How frontend/backend separation is implemented
Frontend and backend are separated at both code and runtime boundaries.

Code-level separation:
- Frontend UI assets:
  - `gui/assets/index.html`
  - `gui/assets/app.js`
  - `gui/assets/styles.css`
- Python backend computation:
  - `core/`, `vmc/`, `dmc/`, `benchmarks/`
- Bridging logic:
  - `gui/app.py` exposes a narrow JS-callable bridge and forwards to
    `application` use-cases.
  - `api/api.py` exposes HTTP endpoints and forwards to the same use-cases.

Runtime-level separation:
- In direct mode, UI talks to local Python bridge (no HTTP required).
- In API mode, UI talks to FastAPI endpoint(s) over HTTP.
- In both paths, business orchestration is shared in `application/`.

Because orchestration is shared, the same simulation request semantics and
result schema are preserved across transports.

### 4. Direct + API fallback mechanism (robustness + flexibility)
`pyqmc gui` supports three compute modes:

- `--compute-mode direct`
  - Force local in-process computation through pywebview JS bridge.
- `--compute-mode api`
  - Force HTTP execution through API endpoint(s).
- `--compute-mode auto` (default)
  - Prefer direct local call.
  - Fall back to API path when direct call is unavailable or fails.
  - If no external API URL is provided, GUI can start an embedded local API
    process and use it as fallback.

Why this design is robust:
- Reduces single points of failure:
  - API startup/network issues do not block local educational usage if direct
    compute works.
  - Bridge limitations do not block usage if API is available.
- Supports diverse deployment environments:
  - Offline teaching/lab machine: direct mode.
  - Shared compute service or remote host: API mode.
  - Mixed/uncertain environment: auto fallback.

Why this design is flexible:
- Transport can be selected per scenario without changing scientific modules.
- The same core computations can run on laptop CPU, remote server, or embedded
  API process with minimal operational changes.
- Future transports (for example batch worker, notebook service, websocket UI)
  can reuse `application` use-cases instead of re-implementing orchestration.

### 5. Why this architecture is a strong role model for other projects
This design is a good reusable template because it provides:

- Clear boundaries and maintainability:
  - Fewer accidental couplings, easier refactoring.
- Testability:
  - Core and use-case layers can be unit-tested without UI/server stacks.
  - Adapter contracts can be integration-tested independently.
- Consistency:
  - One orchestration layer prevents behavior divergence between GUI/API/CLI.
- Evolvability:
  - New methods and systems can be added as domain modules, then exposed
    through existing adapters.
- Operational resilience:
  - Dual execution path (direct + API fallback) keeps workflows running under
    varied runtime constraints.

### 6. Practical extension pattern (recommended)
When adding new functionality, keep this sequence:

1. Add/extend domain solver code in method modules (`vmc/`, `dmc/`, etc.).
2. Add a transport-agnostic use-case in `application/`.
3. Reuse shared mapping/validation helpers in `core/` when possible.
4. Expose the use-case in adapters:
   - CLI command.
   - API route/model.
   - GUI bridge + frontend trigger.
5. Add tests by layer:
   - unit tests for domain/use-case logic.
   - integration tests for adapter contracts.
6. Update docs near each layer and in this manual.

Following this pattern preserves frontend/backend separation while still keeping
the whole project easy to teach, run, and evolve.

## Documentation Index
- API 中文开发详解：
  - `src/pyqmc/api/API_DEVELOPER_GUIDE_ZH.md`
- GUI 中文联动说明：
  - `src/pyqmc/gui/GUI_DEVELOPER_NOTE_ZH.md`
- 基准参考说明：
  - `docs/benchmark_references.md`

## Layer Responsibilities
- `core` / `vmc` / `dmc`:
  - no FastAPI imports
  - no pywebview imports
  - pure simulation and numerical logic
- `application`:
  - transport-agnostic orchestration/use-cases
  - shared entry points for API, GUI direct mode, and CLI
- `api`:
  - pydantic request/response models
  - endpoint handlers that call `application` use-cases
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
3. Add or extend a transport-agnostic use-case in `src/pyqmc/application`.
4. Add CLI command wiring in `src/pyqmc/cli.py` (calling `application`).
5. Add API request/response models and route handlers in `src/pyqmc/api` (calling `application`).
6. Add benchmark references and cases in `src/pyqmc/benchmarks` if relevant.
7. Add unit + integration tests.
8. Update user/developer manuals.

## Coding Conventions
- Prefer explicit types and small focused functions.
- Add docstrings for public functions/classes.
- Add concise comments only where logic is non-obvious.
- Keep reproducibility controls (`seed`) visible at API and CLI boundaries.
