# pyQMC

Educational Quantum Monte Carlo examples with a backend-first design and an optional pywebview GUI.

Current status:
- Phase 1: backend project scaffold + VMC for 1D harmonic oscillator (CLI)
- Phase 2: FastAPI backend service + pywebview GUI shell with separated assets
- Future phases: tests, benchmark suite, full manuals

## Quick start

Standalone backend simulation:
```bash
pip install -e .
pyqmc vmc-ho
```

Run API + GUI (optional dependencies):
```bash
pip install -e '.[api,gui]'
pyqmc gui
```

Run tests:
```bash
pytest
```
