# pyQMC User Manual

## Current Scope (Phase 2)
Phase 2 provides:
- Standalone backend CLI for educational Variational Monte Carlo (VMC).
- FastAPI backend service for programmatic/API usage.
- pywebview GUI frontend that consumes the API.

## Installation (editable)
```bash
pip install -e .
```

To run API and GUI components:
```bash
pip install -e '.[api,gui]'
```

## Run the educational VMC example
```bash
pyqmc vmc-ho
```

Example with custom parameters and JSON output:
```bash
pyqmc vmc-ho --n-steps 30000 --burn-in 5000 --alpha 1.0 --json
```

## Interpreting result
- Exact ground-state energy for this system is 0.5 (in chosen units).
- A correct run should produce an estimate near 0.5 within statistical error.

## Run backend as API service
```bash
pyqmc serve-api --host 127.0.0.1 --port 8000
```

Equivalent dedicated script:
```bash
pyqmc-api --host 127.0.0.1 --port 8000
```

API docs are available at:
- `http://127.0.0.1:8000/docs`

## Run pywebview frontend
Start GUI with embedded local API:
```bash
pyqmc gui
```

Or connect GUI to an already-running API:
```bash
pyqmc gui --api-url http://127.0.0.1:8000
```

## Run tests
```bash
pytest
```

If you use conda:
```bash
conda activate pyqmc
pytest
```

## Next phases
- Phase 3: pytest unit and integration tests
- Phase 4: benchmark suite + complete manuals
