# pyQMC

Educational Quantum Monte Carlo examples with a backend-first design and an optional pywebview GUI.

Current status:
- Phase 1: backend project scaffold + VMC for 1D harmonic oscillator (CLI)
- Phase 2: FastAPI backend service + pywebview GUI shell with separated assets
- Phase 3: pytest unit and integration test suite
- Phase 4: benchmark suite + user/developer manual expansion

## Quick start

Standalone backend simulation:
```bash
pip install -e .
pyqmc vmc-ho
```

Run API + GUI on the same machine (optional dependencies):
```bash
pip install -e '.[api,gui]'
pyqmc gui
```

Run GUI with direct local compute only (no HTTP):
```bash
pyqmc gui --compute-mode direct
```

Run tests:
```bash
pytest
```

Run numerical benchmark suite:
```bash
pyqmc benchmark --strict
```

## Deploying Server and Client on Different Machines

Use this mode when you want a remote machine to be the backend compute engine.

### 1. Deploy backend API server (remote machine)

Install and start API service:
```bash
git clone <your-repo-url>
cd pyQMC
conda env create -f environment.yml
conda activate pyqmc
pip install -e '.[api]'
pyqmc serve-api --host 0.0.0.0 --port 8000
```

Health check from another machine:
```bash
curl http://<SERVER_IP>:8000/health
```

API docs (Swagger):
```text
http://<SERVER_IP>:8000/docs
```

### 2. Deploy client GUI (local desktop machine)

Install GUI dependencies:
```bash
git clone <your-repo-url>
cd pyQMC
conda env create -f environment.yml
conda activate pyqmc
pip install -e '.[gui]'
```

Run GUI against remote backend only:
```bash
pyqmc gui --compute-mode api --api-url http://<SERVER_IP>:8000
```

Run GUI in hybrid mode (direct local compute first, API fallback second):
```bash
pyqmc gui --compute-mode auto --api-url http://<SERVER_IP>:8000
```

### 3. Optional: CLI client against remote API

For remote API testing, you can use `curl` directly. Example:
```bash
curl -X POST http://<SERVER_IP>:8000/simulate/vmc/harmonic-oscillator \
  -H "Content-Type: application/json" \
  -d '{"n_steps":20000,"burn_in":2000,"step_size":1.0,"alpha":1.0,"initial_position":0.0,"seed":12345}'
```

## API Server Entry Points

- Server startup entrypoint:
  - `src/pyqmc/api/api_server.py` (`run_server`)
- HTTP route definitions (request handlers):
  - `src/pyqmc/api/api.py` (`create_app` and `@app.get/@app.post` handlers)

## Deployment Notes

- `--compute-mode direct` needs no HTTP server (fully local).
- `--compute-mode api` requires reachable API URL.
- `--compute-mode auto` provides robustness: direct local compute first, then API fallback.
- For internet-facing deployment, put API behind HTTPS reverse proxy and restrict CORS/auth as needed.
