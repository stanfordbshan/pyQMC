# pyQMC User Manual

## Overview
`pyQMC` is an educational Quantum Monte Carlo application with:
- standalone backend simulation CLI
- FastAPI backend service for API use
- pywebview desktop GUI frontend
- benchmark suite for numerical correctness checks

Current implemented physics scope:
- Method: Variational Monte Carlo (Metropolis)
- System: 1D harmonic oscillator in units `hbar = m = omega = 1`

## Setup

### Conda (recommended)
```bash
conda env create -f environment.yml
conda activate pyqmc
```

### Pip editable install
```bash
pip install -e .
```

To include API + GUI extras:
```bash
pip install -e '.[api,gui]'
```

## CLI Usage

### 1. Run standalone simulation
```bash
pyqmc vmc-ho
```

Example with custom parameters and JSON output:
```bash
pyqmc vmc-ho --n-steps 30000 --burn-in 5000 --alpha 1.0 --json
```

Important output fields:
- `mean_energy`: estimated ground-state energy
- `standard_error`: Monte Carlo uncertainty estimate
- `acceptance_ratio`: Metropolis acceptance fraction

### 2. Run benchmark suite
```bash
pyqmc benchmark
```

Machine-readable output:
```bash
pyqmc benchmark --json
```

Fail CI/script if any benchmark case fails:
```bash
pyqmc benchmark --strict
```

## API Usage

### Start API server
```bash
pyqmc serve-api --host 127.0.0.1 --port 8000
```

Equivalent dedicated entry point:
```bash
pyqmc-api --host 127.0.0.1 --port 8000
```

Swagger docs:
- `http://127.0.0.1:8000/docs`

Key endpoints:
- `GET /health`
- `GET /methods`
- `GET /systems`
- `POST /simulate/vmc/harmonic-oscillator`
- `POST /benchmark/vmc/harmonic-oscillator`

## GUI Usage

Launch GUI with embedded local API backend:
```bash
pyqmc gui
```

Launch GUI connected to an already-running API:
```bash
pyqmc gui --api-url http://127.0.0.1:8000
```

## Testing
Run full unit + integration test suite:
```bash
pytest
```

## Benchmark Interpretation
The benchmark suite compares computed energies to analytic/literature-backed references.

Current benchmark cases:
- `alpha = 1.0`: exact ground-state reference `E0 = 0.5`
- `alpha = 0.8`: variational reference `E(alpha) = 1/4 * (alpha + 1/alpha)`
- `alpha = 1.2`: variational reference `E(alpha) = 1/4 * (alpha + 1/alpha)`

For detailed formulas and references, see:
- `docs/benchmark_references.md`
