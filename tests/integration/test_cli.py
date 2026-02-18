"""Integration tests for the pyqmc command-line entrypoint."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _run_pyqmc(args: list[str]) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[2]
    src_path = repo_root / "src"

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{existing}" if existing else str(src_path)
    )

    cmd = [sys.executable, "-m", "pyqmc", *args]
    return subprocess.run(
        cmd,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_vmc_ho_json_output_contains_expected_fields() -> None:
    proc = _run_pyqmc(
        [
            "vmc-ho",
            "--n-steps",
            "5000",
            "--burn-in",
            "500",
            "--alpha",
            "0.95",
            "--seed",
            "7",
            "--json",
        ]
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)

    assert payload["method"] == "VMC (Metropolis)"
    assert payload["system"] == "harmonic_oscillator_1d"
    assert payload["n_samples"] == 4500
    assert abs(payload["mean_energy"] - 0.5) < 0.05


def test_vmc_ho_invalid_burn_in_returns_nonzero_exit() -> None:
    proc = _run_pyqmc(
        [
            "vmc-ho",
            "--n-steps",
            "100",
            "--burn-in",
            "100",
        ]
    )

    assert proc.returncode != 0
    combined_output = f"{proc.stdout}\n{proc.stderr}"
    assert "burn_in must be smaller than n_steps" in combined_output


def test_top_level_help_lists_supported_commands() -> None:
    proc = _run_pyqmc(["--help"])

    assert proc.returncode == 0
    assert "vmc-ho" in proc.stdout
    assert "serve-api" in proc.stdout
    assert "gui" in proc.stdout
