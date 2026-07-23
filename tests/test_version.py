"""Test de que la versión tiene una única fuente de verdad."""

from importlib.metadata import version

import invisible_friend


def test_version_coincide_con_metadata() -> None:
    """__version__ sale de los metadatos del paquete, no de una copia a mano."""
    assert invisible_friend.__version__ == version("invisible-friend")


def test_version_no_esta_vacia() -> None:
    """El paquete instalado reporta una versión real."""
    assert invisible_friend.__version__
    assert invisible_friend.__version__ != "0.0.0.dev0"
