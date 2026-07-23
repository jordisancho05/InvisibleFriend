"""Amigo Invisible: genera y reparte por email las asignaciones de un sorteo.

La versión es única y vive en `pyproject.toml`; aquí se lee de los metadatos
del paquete instalado en lugar de duplicarla.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("invisible-friend")
except PackageNotFoundError:  # pragma: no cover - solo en un checkout sin instalar
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
