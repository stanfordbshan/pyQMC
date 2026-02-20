"""pywebview host app for the educational pyQMC frontend."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode
from urllib.request import urlopen

from pyqmc.core.config import SimulationConfig
from pyqmc.vmc.solver import run_vmc_harmonic_oscillator

ComputeMode = Literal["auto", "direct", "api"]
COMPUTE_MODE_CHOICES: tuple[ComputeMode, ...] = ("auto", "direct", "api")


@dataclass
class EmbeddedApiProcess:
    """State for an API process launched by the GUI host."""

    process: subprocess.Popen[bytes]
    base_url: str


class LocalComputeBridge:
    """Expose local Python computations directly to frontend JavaScript."""

    def run_vmc_harmonic_oscillator(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run VMC locally without HTTP and return JSON-serializable result."""
        config = _build_vmc_config_from_payload(payload)
        result = run_vmc_harmonic_oscillator(config)
        return result.to_dict()


def _build_vmc_config_from_payload(payload: dict[str, Any]) -> SimulationConfig:
    """Parse and validate GUI payload into `SimulationConfig`."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")

    n_steps = _parse_int(payload.get("n_steps", 20_000), "n_steps")
    burn_in = _parse_int(payload.get("burn_in", 2_000), "burn_in")
    step_size = _parse_float(payload.get("step_size", 1.0), "step_size")
    alpha = _parse_float(payload.get("alpha", 1.0), "alpha")
    initial_position = _parse_float(
        payload.get("initial_position", 0.0),
        "initial_position",
    )

    raw_seed = payload.get("seed", 12345)
    seed: int | None
    if raw_seed in (None, ""):
        seed = None
    else:
        seed = _parse_int(raw_seed, "seed")

    return SimulationConfig(
        n_steps=n_steps,
        burn_in=burn_in,
        step_size=step_size,
        alpha=alpha,
        initial_position=initial_position,
        seed=seed,
    )


def _parse_int(value: Any, field_name: str) -> int:
    """Parse one integer field from GUI payload."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


def _parse_float(value: Any, field_name: str) -> float:
    """Parse one float field from GUI payload."""
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number") from exc


def _wait_for_api_health(base_url: str, timeout_seconds: float = 15.0) -> None:
    """Poll `/health` until the API is reachable or timeout elapses."""
    deadline = time.time() + timeout_seconds
    health_url = f"{base_url.rstrip('/')}/health"
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with urlopen(health_url, timeout=1.0) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # pragma: no cover - thin startup wrapper
            last_error = exc
            time.sleep(0.2)

    if last_error is not None:
        raise RuntimeError(
            f"API server at {base_url} did not become ready in {timeout_seconds:.1f}s: {last_error}"
        )
    raise RuntimeError(
        f"API server at {base_url} did not become ready in {timeout_seconds:.1f}s"
    )


def _start_embedded_api(host: str, port: int) -> EmbeddedApiProcess:
    """Start an API subprocess for GUI API-mode/fallback use."""
    base_url = f"http://{host}:{port}"
    cmd = [
        sys.executable,
        "-m",
        "pyqmc.api.api_server",
        "--host",
        host,
        "--port",
        str(port),
    ]

    process = subprocess.Popen(  # noqa: S603 - controlled local command
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_api_health(base_url)
    except Exception as exc:
        _stop_embedded_api(EmbeddedApiProcess(process=process, base_url=base_url))
        raise RuntimeError(
            "Failed to start embedded API. Ensure API deps are installed with: "
            "pip install -e '.[api,gui]'"
        ) from exc

    return EmbeddedApiProcess(process=process, base_url=base_url)


def _stop_embedded_api(embedded: EmbeddedApiProcess | None) -> None:
    """Stop an embedded API process if it is still running."""
    if embedded is None:
        return

    process = embedded.process
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:  # pragma: no cover - fallback path
        process.kill()
        process.wait(timeout=3.0)


def _resolve_api_backend(
    compute_mode: ComputeMode,
    api_url: str | None,
    api_host: str,
    api_port: int,
) -> tuple[EmbeddedApiProcess | None, str | None]:
    """Resolve API fallback URL and embedded API process state."""
    if compute_mode == "direct":
        return None, None

    if api_url is not None:
        _wait_for_api_health(api_url)
        return None, api_url

    embedded = _start_embedded_api(api_host, api_port)
    return embedded, embedded.base_url


def _build_frontend_url(
    api_base_url: str | None,
    compute_mode: ComputeMode,
) -> str:
    """Return file URL for frontend with compute/API mode query params."""
    assets_dir = Path(__file__).resolve().parent / "assets"
    index_file = assets_dir / "index.html"

    if not index_file.exists():
        raise RuntimeError(f"GUI asset is missing: {index_file}")

    query_params: dict[str, str] = {"compute_mode": compute_mode}
    if api_base_url is not None:
        query_params["api_base_url"] = api_base_url

    query = urlencode(query_params)
    return f"{index_file.resolve().as_uri()}?{query}"


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser for GUI startup."""
    parser = argparse.ArgumentParser(
        prog="pyqmc-gui",
        description="Run the pyQMC pywebview frontend",
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="Use an existing pyQMC API URL instead of starting an embedded API",
    )
    parser.add_argument(
        "--compute-mode",
        default="auto",
        choices=COMPUTE_MODE_CHOICES,
        help=(
            "Computation transport mode: 'direct' uses local Python bridge only, "
            "'api' uses HTTP API only, 'auto' tries direct first and falls back to API"
        ),
    )
    parser.add_argument("--api-host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--width", type=int, default=1180)
    parser.add_argument("--height", type=int, default=820)
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable pywebview debug mode",
    )
    return parser


def launch_gui(
    api_url: str | None = None,
    compute_mode: ComputeMode = "auto",
    api_host: str = "127.0.0.1",
    api_port: int = 8000,
    width: int = 1180,
    height: int = 820,
    debug: bool = False,
) -> int:
    """Launch pywebview with direct local compute and/or API fallback."""
    try:
        import webview
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing GUI dependencies. Install with: pip install -e '.[gui]'"
        ) from exc

    embedded, resolved_api_url = _resolve_api_backend(
        compute_mode=compute_mode,
        api_url=api_url,
        api_host=api_host,
        api_port=api_port,
    )

    frontend_url = _build_frontend_url(
        api_base_url=resolved_api_url,
        compute_mode=compute_mode,
    )

    window = webview.create_window(
        title="pyQMC Educational GUI",
        url=frontend_url,
        js_api=LocalComputeBridge(),
        width=width,
        height=height,
        min_size=(980, 680),
    )

    def _on_window_closed() -> None:
        _stop_embedded_api(embedded)

    window.events.closed += _on_window_closed

    try:
        webview.start(debug=debug)
    finally:
        _stop_embedded_api(embedded)

    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for GUI launcher."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return launch_gui(
            api_url=args.api_url,
            compute_mode=args.compute_mode,
            api_host=args.api_host,
            api_port=args.api_port,
            width=args.width,
            height=args.height,
            debug=args.debug,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
