"""Integration tests for FastAPI routes using in-process TestClient."""

from __future__ import annotations

from fastapi.testclient import TestClient

from pyqmc.api.api import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_catalog_endpoints() -> None:
    client = TestClient(create_app())

    methods_resp = client.get("/methods")
    systems_resp = client.get("/systems")

    assert methods_resp.status_code == 200
    assert systems_resp.status_code == 200

    methods = methods_resp.json()
    systems = systems_resp.json()

    assert methods and methods[0]["id"] == "vmc_metropolis"
    assert systems and systems[0]["id"] == "harmonic_oscillator_1d"


def test_simulation_endpoint_returns_expected_payload() -> None:
    client = TestClient(create_app())

    payload = {
        "n_steps": 5000,
        "burn_in": 500,
        "step_size": 1.0,
        "alpha": 0.95,
        "initial_position": 0.0,
        "seed": 7,
    }

    response = client.post("/simulate/vmc/harmonic-oscillator", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "harmonic_oscillator_1d"
    assert data["n_samples"] == 4500
    assert abs(data["mean_energy"] - 0.5) < 0.05
    assert data["metadata"]["exact_ground_state_energy"] == 0.5


def test_simulation_endpoint_validates_burnin() -> None:
    client = TestClient(create_app())

    payload = {
        "n_steps": 100,
        "burn_in": 100,
        "step_size": 1.0,
        "alpha": 1.0,
        "initial_position": 0.0,
        "seed": 7,
    }

    response = client.post("/simulate/vmc/harmonic-oscillator", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"]
