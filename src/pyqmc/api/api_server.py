"""API server entrypoint wrapping uvicorn startup."""

from __future__ import annotations

import argparse
import importlib.util
import sys


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser for API server startup."""
    parser = argparse.ArgumentParser(
        prog="pyqmc-api",
        description="Run the pyQMC FastAPI server",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--log-level", default="info")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for local development",
    )
    return parser


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    log_level: str = "info",
    reload: bool = False,
) -> None:
    """Run uvicorn with the pyQMC app factory."""
    if importlib.util.find_spec("fastapi") is None:
        raise RuntimeError(
            "Missing API dependencies. Install with: pip install -e '.[api]'"
        )

    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing API dependencies. Install with: pip install -e '.[api]'"
        ) from exc

    uvicorn.run(
        "pyqmc.api.api:create_app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
        factory=True,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for API server."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
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


if __name__ == "__main__":
    raise SystemExit(main())
