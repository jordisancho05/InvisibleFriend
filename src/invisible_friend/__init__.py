"""Invisible Friend: generate and deliver a Secret Santa draw by email.

The version has a single source of truth in `pyproject.toml`; here it is read
from the installed package metadata instead of being duplicated.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("invisible-friend")
except PackageNotFoundError:  # pragma: no cover - only in an uninstalled checkout
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
