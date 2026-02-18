"""HTTP API package for pyQMC.

Importing this package should not require optional FastAPI dependencies.
"""

__all__ = ["create_app"]


def create_app():
    """Lazily import and return the FastAPI app factory."""
    from .api import create_app as _create_app

    return _create_app()
