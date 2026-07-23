"""Lanzador desde la raíz del proyecto.

Equivale a `python -m invisible_friend` y al script `invisible-friend`:

    python main.py              # simula el envío (por defecto)
    python main.py --enviar     # envía los emails de verdad
"""

import sys

from invisible_friend.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
