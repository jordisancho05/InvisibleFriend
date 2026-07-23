"""Launcher from the project root.

Equivalent to `python -m invisible_friend` and the `invisible-friend` script:

    python main.py            # simulate the delivery (default)
    python main.py --send     # actually send the emails
"""

import sys

from invisible_friend.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
