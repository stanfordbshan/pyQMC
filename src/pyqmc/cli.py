"""Command-line interface for running backend simulations and services."""

from __future__ import annotations

import argparse
import json
import sys

from pyqmc.core.config import SimulationConfig
from pyqmc.vmc.solver import run_vmc_harmonic_oscillator


def build_parser() -> argparse.ArgumentParser:
    """Build top-level CLI parser."""
    parser = argparse.ArgumentParser(
        prog="pyqmc",
        description="Educational Quantum Monte Carlo toolkit",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    vmc_ho = subparsers.add_parser(
        "vmc-ho",
        help="Run VMC for the 1D harmonic oscillator",
    )
    vmc_ho.add_argument("--n-steps", type=int, default=20_000)
    vmc_ho.add_argument("--burn-in", type=int, default=2_000)
    vmc_ho.add_argument("--step-size", type=float, default=1.0)
    vmc_ho.add_argument("--alpha", type=float, default=1.0)
    vmc_ho.add_argument("--initial-position", type=float, default=0.0)
    vmc_ho.add_argument("--seed", type=int, default=12345)
    vmc_ho.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text summary",
    )

    serve_api = subparsers.add_parser(
        "serve-api",
        help="Run FastAPI backend service",
    )
    serve_api.add_argument("--host", default="127.0.0.1")
    serve_api.add_argument("--port", type=int, default=8000)
    serve_api.add_argument("--log-level", default="info")
    serve_api.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for local development",
    )

    gui = subparsers.add_parser(
        "gui",
        help="Launch pywebview frontend",
    )
    gui.add_argument(
        "--api-url",
        default=None,
        help="Use an existing API URL instead of starting an embedded backend",
    )
    gui.add_argument("--api-host", default="127.0.0.1")
    gui.add_argument("--api-port", type=int, default=8000)
    gui.add_argument("--width", type=int, default=1180)
    gui.add_argument("--height", type=int, default=820)
    gui.add_argument("--debug", action="store_true")

    return parser


def _run_vmc_ho(args: argparse.Namespace) -> int:
    config = SimulationConfig(
        n_steps=args.n_steps,
        burn_in=args.burn_in,
        step_size=args.step_size,
        alpha=args.alpha,
        initial_position=args.initial_position,
        seed=args.seed,
    )

    result = run_vmc_harmonic_oscillator(config)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.to_pretty_text())

    return 0


def _run_serve_api(args: argparse.Namespace) -> int:
    try:
        from pyqmc.api.api_server import run_server

        run_server(
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return 0


def _run_gui(args: argparse.Namespace) -> int:
    try:
        from pyqmc.gui.app import launch_gui

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


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "vmc-ho":
        return _run_vmc_ho(args)
    if args.command == "serve-api":
        return _run_serve_api(args)
    if args.command == "gui":
        return _run_gui(args)

    parser.error(f"unsupported command: {args.command}")
    return 2
