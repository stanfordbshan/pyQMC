"""pywebview host app for the educational pyQMC frontend."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


@dataclass
class EmbeddedApiProcess:
    """State for an API process launched by the GUI host."""

    process: subprocess.Popen[bytes]
    base_url: str


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
    """Start an API subprocess for the GUI to consume."""
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


def _build_frontend_url(api_base_url: str) -> str:
    """Return a file URL for the frontend with API endpoint in query params."""
    assets_dir = Path(__file__).resolve().parent / "assets"
    index_file = assets_dir / "index.html"

    if not index_file.exists():
        raise RuntimeError(f"GUI asset is missing: {index_file}")

    query = urlencode({"api_base_url": api_base_url})
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
    api_host: str = "127.0.0.1",
    api_port: int = 8000,
    width: int = 1180,
    height: int = 820,
    debug: bool = False,
) -> int:
    """Launch pywebview with either embedded or external API backend."""
    try:
        import webview
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing GUI dependencies. Install with: pip install -e '.[gui]'"
        ) from exc

    embedded: EmbeddedApiProcess | None = None
    resolved_api_url = api_url

    if resolved_api_url is None:
        embedded = _start_embedded_api(api_host, api_port)
        resolved_api_url = embedded.base_url
    else:
        _wait_for_api_health(resolved_api_url)

    frontend_url = _build_frontend_url(resolved_api_url)

    window = webview.create_window(
        title="pyQMC Educational GUI",
        url=frontend_url,
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
